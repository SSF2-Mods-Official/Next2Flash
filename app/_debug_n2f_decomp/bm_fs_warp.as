package {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class bm_fs_warp extends MovieClip {
        public function bm_fs_warp() {
            super();
            addFrameScript(10, frame_11);
        }
        internal function frame_11():* {
            stop();
                        if (parent != null)
                        {
                            parent.removeChild(this);
                        };
        }
    }
}
