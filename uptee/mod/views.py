import os
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST
from annoying.decorators import ajax_request
from mod.forms import ChangeModForm, MapUploadForm, ModeratorForm, ServerDescriptionForm
from mod.models import Map, Option, Server, Vote
from settings import MEDIA_ROOT


def server_list(request, username=None, server_status=None):
    if username:
        user = get_object_or_404(User.objects.filter(is_active=True), username=username)
        servers = Server.active.filter(owner=user)
    else:
        servers = Server.active.all()
    if server_status:
        online = True if server_status == 'online' else False
        servers = (server for server in servers if server.is_online == online)
    return render_to_response('mod/servers.html', {
        'server_list': servers,
        'username': username,
        'server_type': server_status
    }, context_instance=RequestContext(request))


def server_detail(request, server_id):
    server = get_object_or_404(Server.active.select_related(), pk=server_id)
    moderator = server.moderators.filter(user=request.user) if request.user.is_authenticated() else None
    moderator = moderator[0] if moderator else None
    return render_to_response('mod/server_detail_info.html', {
        'server': server,
        'moderator': moderator
    }, context_instance=RequestContext(request))


@login_required
def server_edit_description(request, server_id):
    server = get_object_or_404(Server.active.select_related().filter(owner=request.user), pk=server_id)
    form = ServerDescriptionForm(instance=server)
    if request.method == 'POST':
        form = ServerDescriptionForm(request.POST, instance=server)
        if form.is_valid():
            form.save()
            next = request.REQUEST.get('next', reverse('server_detail', kwargs={'server_id': server.id}))
            return render_to_response('mod/description_updated.html', {'next': next}, context_instance=RequestContext(request))
    return render_to_response('mod/server_edit_description.html', {
        'server': server,
        'description_form': form
    }, context_instance=RequestContext(request))


@login_required
def server_moderators(request, server_id):
    server = get_object_or_404(Server.active.select_related().filter(owner=request.user), pk=server_id)
    form = ModeratorForm(request.user, server)
    if request.method == 'POST':
        form = ModeratorForm(request.user, server, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Moderator successfully added.')
    return render_to_response('mod/server_detail_moderators.html', {
        'server': server,
        'moderator_form': form,
        'moderator': None
    }, context_instance=RequestContext(request))


@login_required
def server_edit_moderator(request, server_id, user_id):
    server = get_object_or_404(Server.active.select_related().filter(owner=request.user), pk=server_id)
    moderator = get_object_or_404(server.moderators.select_related(), user__pk=user_id)
    if request.method == 'POST':
        if 'form-delete-moderator' in request.POST.keys():
            moderator.delete()
            messages.success(request, 'Moderator successfully deleted.')
            return redirect(reverse(server_moderators, kwargs={'server_id': server.pk}))
        if 'restart_allowed' in request.POST.keys():
            moderator.restart_allowed = True
        else:
            moderator.restart_allowed = False
        if 'edit_votes_allowed' in request.POST.keys():
            moderator.edit_votes_allowed = True
        else:
            moderator.edit_votes_allowed = False
        if 'map_upload_allowed' in request.POST.keys():
            moderator.map_upload_allowed = True
        else:
            moderator.map_upload_allowed = False
        for option in moderator.allowed_options.all():
            if option.command not in request.POST.keys():
                moderator.allowed_options.remove(option)
        for tune in moderator.allowed_tunings.all():
            if tune.command not in request.POST.keys():
                moderator.allowed_tunings.remove(tune)
        for key in request.POST.keys():
            if key == 'csrfmiddlewaretoken':
                continue
            option = moderator.allowed_options.filter(command=key)
            if not option:
                option = server.config_options.filter(command=key)
                if option:
                    moderator.allowed_options.add(option[0])
            else:
                continue
            tune = moderator.allowed_tunings.filter(command=key)
            if not tune:
                tune = server.config_tunes.filter(command=key)
                if tune:
                    moderator.allowed_tunings.add(tune[0])
        moderator.save()
        messages.success(request, 'Moderator successfully updated.')
    return render_to_response('mod/server_edit_moderator.html', {
        'server': server,
        'moderator_settings': moderator,
        'moderator': None
    }, context_instance=RequestContext(request))


@login_required
def server_edit(request, server_id):
    server = get_object_or_404(Server.active.select_related(), pk=server_id)
    moderator = server.moderators.filter(user=request.user)
    if server.owner != request.user and not moderator:
        raise Http404
    moderator = moderator[0] if moderator else None
    if server.owner != request.user and moderator:
        options = moderator.allowed_options.all()
        if not options:
            raise Http404
    else:
        options = server.config_options.all()
    return render_to_response('mod/server_detail_edit.html', {
        'server': server,
        'options': options,
        'moderator': moderator
    }, context_instance=RequestContext(request))


@login_required
def upload_map(request, server_id):
    server = get_object_or_404(Server.active.select_related(), pk=server_id)
    moderator = server.moderators.filter(user=request.user)
    if server.owner != request.user and (not moderator or not moderator[0].map_upload_allowed):
        raise Http404
    moderator = moderator[0] if moderator else None
    if request.method == 'POST':
        form = MapUploadForm(request.POST, request.FILES)
        if form.is_valid():
            map_file = form.cleaned_data['map_file']
            mod_name = server.mod.title
            maps_path = os.path.join(MEDIA_ROOT, 'mods', mod_name, 'servers', server.owner.username, '{0}'.format(server_id), 'maps')
            if not os.path.exists(maps_path):
                os.makedirs(maps_path)
            with open(os.path.join(maps_path, map_file.name), 'wb') as f:
                f.write(map_file.read())
            map_obj = Map(server=server, name=os.path.splitext(map_file.name)[0])
            map_obj.save()
            messages.success(request, 'Map was successfully uploaded.')
    else:
        form = MapUploadForm()
    return render_to_response('mod/server_detail_upload_map.html', {
        'server': server,
        'form': form,
        'moderator': moderator
    }, context_instance=RequestContext(request))


def map_download(request, map_id):
    map_obj = get_object_or_404(Map, pk=map_id)
    password = map_obj.server.config_options.filter(command='password')
    if password:
        password = password[0].value
    if request.user != map_obj.server.owner and password:
        raise Http404
    map_path = map_obj.get_download_url()
    if not map_path:
        raise Http404
    map_obj.download_count += 1
    map_obj.save()
    map_name = os.path.basename(map_path)
    fsock = open(map_path, 'rb')
    response = HttpResponse(fsock, mimetype='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(map_name)
    return response


def map_details(request, map_id):
    map_obj = get_object_or_404(Map, pk=map_id)
    return render_to_response('mod/map_details.html', {
        'map_obj': map_obj,
    }, context_instance=RequestContext(request))


@login_required
@require_POST
def delete_map(request, map_id):
    map_obj = get_object_or_404(Map, pk=map_id)
    if map_obj.server.owner != request.user:
        raise Http404
    next = request.REQUEST.get('next', reverse('server_detail', kwargs={'server_id': map_obj.server.id}))
    map_obj.delete()
    return render_to_response('mod/map_deleted.html', {'next': next}, context_instance=RequestContext(request))


@login_required
def server_edit_votes(request, server_id):
    server = get_object_or_404(Server.active.select_related(), pk=server_id)
    moderator = server.moderators.filter(user=request.user)
    if server.owner != request.user and (not moderator or not moderator[0].edit_votes_allowed):
        raise Http404
    moderator = moderator[0] if moderator else None
    if request.method == 'POST':
        vote = Vote(server=server, command='command', title='New vote')
        vote.save()
    votes = server.config_votes.all()
    return render_to_response('mod/server_detail_edit_votes.html', {
        'server': server,
        'votes': votes,
        'moderator': moderator
    }, context_instance=RequestContext(request))


@login_required
def server_tunes(request, server_id):
    server = get_object_or_404(Server.active.select_related(), pk=server_id)
    moderator = server.moderators.filter(user=request.user)
    if server.owner != request.user and not moderator:
        raise Http404
    moderator = moderator[0] if moderator else None
    if server.owner != request.user and moderator:
        tunes = moderator.allowed_tunings.all()
        if not tunes:
            raise Http404
    else:
        tunes = server.config_tunes.all()
    if not tunes:
        raise Http404
    return render_to_response('mod/server_detail_tunes.html', {
        'server': server,
        'tunes': tunes,
        'moderator': moderator
    }, context_instance=RequestContext(request))


@login_required
def server_change_mod(request, server_id):
    server = get_object_or_404(Server.active.select_related().filter(owner=request.user), pk=server_id)
    if request.method == 'POST':
        form = ChangeModForm(request.POST, instance=server)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mod was successfully changed.')
    else:
        form = ChangeModForm(initial={'mod': server.mod.pk})
    return render_to_response('mod/server_detail_change_mod.html', {
        'server': server,
        'form': form,
        'moderator': None
    }, context_instance=RequestContext(request))


def server_votes(request, server_id):
    server = get_object_or_404(Server.active.select_related(), pk=server_id)
    moderator = server.moderators.filter(user=request.user) if request.user.is_authenticated() else None
    moderator = moderator[0] if moderator else None
    votes = server.config_votes.all()
    if not votes:
        raise Http404
    return render_to_response('mod/server_detail_votes.html', {
        'server': server,
        'votes': votes,
        'moderator': moderator
    }, context_instance=RequestContext(request))


@login_required
@require_POST
def start_stop_server(request, server_id):
    server = get_object_or_404(Server.active.select_related(), pk=server_id)
    moderator = server.moderators.filter(user=request.user)
    if server.owner != request.user and not request.user.is_staff() and (not moderator or not moderator[0].restart_allowed):
        raise Http404
    next = request.REQUEST.get('next', reverse('user_server_list', kwargs={'username': server.owner.username}))
    map_exists = True
    server.check_online()
    if server.is_online:
        server.set_offline()
    else:
        if server.map_exists:
            server.set_online()
        else:
            map_exists = False
    return render_to_response('mod/state_changed.html', {'next': next, 'map_exists': map_exists}, context_instance=RequestContext(request))


@login_required
@require_POST
def update_settings(request, server_id):
    server = get_object_or_404(Server.active.select_related(), pk=server_id)
    moderator = server.moderators.filter(user=request.user)
    if server.owner != request.user and not moderator:
        raise Http404
    moderator = moderator[0] if moderator else None
    next = request.REQUEST.get('next', reverse('server_edit', kwargs={'server_id': server.id}))
    options = server.config_options.exclude(widget=Option.WIDGET_CHECKBOX)
    for key in request.POST.keys():
        if server.owner != request.user:
            if not moderator.allowed_options.filter(command=key):
                continue
        option = options.filter(command=key)[0] if options.filter(command=key) else None
        if option:
            if option.widget == Option.WIDGET_TEXTAREA:
                option.value = request.POST[key].replace('\r\n', r'\n')
            else:
                option.value = request.POST[key]
            option.save()
    options = server.config_options.filter(widget=Option.WIDGET_CHECKBOX)
    for option in options:
        if option.command in request.POST.keys():
            option.value = '1'
        else:
            option.value = '0'
        option.save()
    return render_to_response('mod/settings_updated.html', {'next': next}, context_instance=RequestContext(request))


@login_required
@require_POST
def update_votes(request, server_id):
    server = get_object_or_404(Server.active.select_related(), pk=server_id)
    moderator = server.moderators.filter(user=request.user)
    if server.owner != request.user and not moderator:
        raise Http404
    moderator = moderator[0] if moderator else None
    if server.owner != request.user and not moderator.edit_votes_allowed:
        raise Http404
    next = request.REQUEST.get('next', reverse('server_edit_votes', kwargs={'server_id': server.id}))
    votes = server.config_votes.all()
    post = request.POST.copy()
    id_done_list = []
    title_done_list = []
    for key in post:
        if ' ' not in key:
            continue
        input_type = key.split(' ', 1)[0]
        if input_type not in ['title', 'command']:
            continue
        vote_id = key.rsplit(' ', 1)[-1]
        if vote_id == 'new':
            if not post[key]:
                continue
            vote_id = key.rsplit(' ', 2)[-2]
            if vote_id in id_done_list:
                continue
            if vote_id.isdigit:
                if input_type == 'title':
                    if post[key] in title_done_list:
                        continue
                    other = 'command'
                else:
                    other = 'title'
                vars()[input_type] = post[key]
                for _key in post:
                    if not post[_key] and ' ' not in _key:
                        continue
                    if _key.rsplit(' ', 1)[-1] == 'new' and _key.split(' ', 1)[0] == other:
                        check_id = key.rsplit(' ', 2)[-2]
                        if check_id == vote_id:
                            if input_type == 'command':
                                if post[_key] in title_done_list:
                                    break
                            vars()[other] = post[_key]
                            new_vote = Vote(server=server, command=vars()['command'], title=vars()['title'])
                            new_vote.save()
                            id_done_list.append(vote_id)
                            title_done_list.append(vars()['title'])
                            break
        elif vote_id.isdigit():
            if input_type == 'title':
                vote = votes.filter(title=post[key]).exclude(pk=vote_id)
                if vote:
                    vote.delete()
            vote = votes.filter(pk=vote_id)
            if len(vote) != 1:
                continue
            vote = vote[0]
            if not post[key]:
                vote.delete()
            else:
                setattr(vote, input_type, post[key])
                vote.save()
    """for vote in votes:
        vote_list = votes.filter(title=vote.title)
        if len(vote_list) > 1:
            vote_list = vote_list[1:]
            for item in vote_list:
                item.delete()"""
    return render_to_response('mod/settings_updated.html', {'next': next}, context_instance=RequestContext(request))


@login_required
@require_POST
def update_tunes(request, server_id):
    server = get_object_or_404(Server.active.select_related(), pk=server_id)
    moderator = server.moderators.filter(user=request.user)
    if server.owner != request.user and not moderator:
        raise Http404
    moderator = moderator[0] if moderator else None
    next = request.REQUEST.get('next', reverse('server_tunes', kwargs={'server_id': server.id}))
    tunes = server.config_tunes.all()
    if tunes:
        for key in request.POST.keys():
            if server.owner != request.user:
                if not moderator.allowed_tunings.filter(command=key):
                    continue
            tune = tunes.filter(command=key)[0] if tunes.filter(command=key) else None
            if tune:
                try:
                    tune.value = float(request.POST[key])
                except ValueError:
                    continue
                tune.save()
    return render_to_response('mod/settings_updated.html', {'next': next}, context_instance=RequestContext(request))


@ajax_request
def server_info_update_ajax(request, server_id):
    if not request.is_ajax():
        raise Http404
    server = get_object_or_404(Server.active.select_related(), pk=server_id)
    server_info = server.info
    if server_info:
        server_info = server.info.server_info
    return {'server_info': server_info}
