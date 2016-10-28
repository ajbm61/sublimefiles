import os
import webbrowser
import glob
import re


import sublime
import sublime_plugin


def man_path(window):
    view = window.active_view()
    if not view:
        return None

    path = view.settings().get('man.path')
    if not path:
        return None

    env_projects_path = os.getenv('PROJECTS_PATH')
    if env_projects_path:
        if not os.path.isdir(env_projects_path):
            raise RuntimeError('PROJECTS_PATH env is not a valid directory')

        path = path.replace('${PROJECTS_PATH}', env_projects_path)

    if not path:
        return None

    if not os.path.isdir(path):
        return None

    return path


def is_php_identifier(value):
    return re.match('^[a-zA-Z_][a-zA-Z0-9_]*$', value)


class ManCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.manuals = self.manuals()
        self.window.show_quick_panel(self.manuals[1], self.on_done)

    def on_done(self, index):
        if index == -1:
            return

        manual = self.manuals[0][index]

        if os.path.isfile(manual):
            webbrowser.open_new_tab('file://%s' % (manual))

    def manuals(self):
        manual_paths = []
        manual_names = []
        path = man_path(self.window)
        if path and os.path.isdir(path):
            for manual_path in glob.glob(path + '/*/index.html'):
                re_match_res = re.match('^.*\/([a-zA-Z0-9-_.]+)\/index.html$', manual_path)
                if re_match_res:
                    manual_paths.append(manual_path)
                    manual_names.append(re_match_res.group(1))

        return (manual_paths, manual_names)


class GotoPhpManCommand(sublime_plugin.WindowCommand):

    def run(self, remote = False):
        view = self.window.active_view()
        if not view:
            return

        symbol = view.substr(view.word(view.sel()[0]))
        if not is_php_identifier(symbol):
            return

        symbol = symbol.replace('_', '-').lower()

        if remote:
            self.goto_remote(symbol)
        else:
            self.goto_local(symbol)

    def goto_remote(self, symbol):
        webbrowser.open_new_tab('https://secure.php.net/%s' % symbol)

    def goto_local(self, symbol):
        path = man_path(self.window)
        if not path:
            return

        def open_file_in_browser(filename):
            if os.path.isfile(filename):
                webbrowser.open_new_tab('file://%s' % filename)
            else:
                sublime.status_message('goto_php_manual: file not found: %s' % filename)

        # https://secure.php.net/urlhowto.php
        open_file_in_browser('%s/php/language.types.%s.html' % (path, symbol))
        open_file_in_browser('%s/php/control-structures.%s.html' % (path, symbol))
        open_file_in_browser('%s/php/book.%s.html' % (path, symbol))
        open_file_in_browser('%s/php/class.%s.html' % (path, symbol))
        open_file_in_browser('%s/php/function.%s.html' % (path, symbol))
