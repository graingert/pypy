from rpython.memory.gctransform.framework import (
     BaseFrameworkGCTransformer, BaseRootWalker, sizeofaddr)


class StmFrameworkGCTransformer(BaseFrameworkGCTransformer):

    def build_root_walker(self):
        return StmRootWalker(self)

    def push_roots(self, hop, keep_current_args=False):
        livevars = self.get_livevars_for_roots(hop, keep_current_args)
        self.num_pushs += len(livevars)
        for var in livevars:
            hop.genop("stm_push_root", [var])
        return livevars

    def pop_roots(self, hop, livevars):
        for var in reversed(livevars):
            hop.genop("stm_pop_root_into", [var])

    def gc_header_for(self, obj, needs_hash=False):
        return self.gcdata.gc.gcheaderbuilder.header_of_object(obj)


class StmRootWalker(BaseRootWalker):

    def need_thread_support(self, gctransform, getfn):
        pass

    def walk_stack_roots(self, collect_stack_root):
        raise NotImplementedError
