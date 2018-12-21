
#
# Copyright 2016-2018 David J. Beal, All Rights Reserved
#

class Debug(object):
    import ast
    import inspect

    from .Colors import Colors

    _ast_cache = {}

    @classmethod
    def propagate_walk(self, roots, recur):
        s = list(roots)
        while len(s):
            yield s
            s = [n for e in s for n in recur(e)]

    @classmethod
    def create_graph_from_ast(self, root, lines):
        import networkx as nx
        g = self.nx.DiGraph()
        for edges in self.propagate_walk([(None, root)], lambda ab: [(ab[1], b) for b in self.ast.iter_child_nodes(ab[1])]):
            for ab in edges:
                if all(hasattr(n, 'lineno') for n in ab):
                    for n in ab:
                        line = lines[n.lineno - 1]
                        g.add_node(n.lineno, {'source': line})
                        if line.strip().startswith('def '):
                            print(str(n.lineno) + ' ' + line)
                    if ab[0] != ab[1]:
                        g.add_path(n.lineno for n in ab)
        return g

    @classmethod
    def get_source_line_graph(self, source_path):
        if source_path not in self._ast_cache:
            try:
                with open(source_path) as infile:
                    source = open(source_path).read()
            except IOError as e:
                print('cannot open: ' + str(source_path))
                result = None
            else:
                lines = source.split('\n')
                root = self.ast.parse(source)
                self.ast.fix_missing_locations(root)
                graph = self.create_graph_from_ast(root, lines)
                result = graph

            self._ast_cache[source_path] = result

        result = self._ast_cache[source_path]
        return result

    @classmethod
    def show_args(self):
        frame = self.inspect.currentframe().f_back

        # show abbreviated backtrace

        back = frame.f_back
        assert back is not None

        if 0:
            # use AST to display containing class of calling function
            frame_path = frame.f_code.co_filename

            graph = self.get_source_line_graph(frame_path)

            lineno = frame.f_lineno
            in_edges = graph.in_edges(lineno)
            print('lineno', lineno, 'in_edges', in_edges)

        if 1:
            # get source lines for frames
            depth = 3
            #
            lines = []
            module_names = []
            frames = []
            current_lines = []
            #
            f = frame
            for i in range(depth):
                if f is not None:
                    #
                    try:
                        (f_lines, f_start) = self.inspect.getsourcelines(f)
                    except IOError as e:
                        f_lines = ['<unknown call location>']
                        f_start = 1

                    linedict = dict(zip(range(f_start, f_start + len(f_lines)), f_lines))

                    lines.append(linedict)

                    module = self.inspect.getmodule(f)

                    if module is not None:
                        module_name = module.__name__
                    else:
                        module_name = '<unknown module>'

                    module_names.append(module_name)

                    frames.append(f)

                    current_lines.append(linedict.get(f.f_lineno, '<cannot fetch source at f_lineno>').strip())

                    f = f.f_back

        if 0:
            back_module = self.inspect.getmodule(back)

            if back_module is not None:
                back_module_name = back_module.__name__
            else:
                back_module_name = '<unknown module>'

        #####

        av = self.inspect.getargvalues(frame)

        # print(av)
        # (args, varargs, varkw, locals) = av

        # av.args
        # av.varargs
        # av.keywords
        # av.locals

        allargs = list(av.args)

        if av.varargs is not None:
            allargs += [av.varargs]

        if av.keywords is not None:
            allargs += [av.keywords]

        values = [av.locals[k] for k in allargs]

        argitems = zip(allargs, values)

        # def repr_with_class_name(o):
        #     return repr(o) + ' <- ' + repr(type(o))

        # argdesc = '\n'.join(tuple('\t\t' + str(n) + ' = ' + repr_with_class_name(v) for (n, v) in argitems))

        dfl = lambda n: n

        nmap = {
            av.varargs: lambda n: '*' + dfl(n),
            av.keywords: lambda n: '**' + dfl(n),
        }

        argitems = [(nmap.get(n, dfl)(n), v) for (n, v) in argitems]

        sp = '    '

        msg = []

        msg += [
            [
                sp * 1,
                self.Colors.GREY,
                module_names[i],
                ': ',
                self.Colors.GREEN,
                frames[i].f_code.co_name,
                self.Colors.NORM,
                ': ',
                self.Colors.WHITE,
                frames[i].f_lineno,
                self.Colors.NORM,
                ': ',
                self.Colors.BLUE,
                current_lines[i],
                self.Colors.NORM,
            ]
            for i in reversed(range(len(frames)))
            #[
            #    sp * 2,
            #    self.Colors.YELLOW,
            #    func_line.strip(),
            #    self.Colors.NORM,
            #],
        ]

        msg += [
            [
                sp * 3,
                self.Colors.WHITE,
                str(n),
                self.Colors.NORM,
                ' = ',
                repr(v),
                # ' <- ',
                # self.Colors.GREEN,
                # repr(type(v)),
                # self.Colors.NORM,
            ]
            for (n, v) in argitems
        ]

        print('\n'.join(''.join(map(str, line)) for line in msg) + '\n')

        # print(msg)


