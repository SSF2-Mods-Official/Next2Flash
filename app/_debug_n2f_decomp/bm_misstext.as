package {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class bm_misstext extends MovieClip {
        public function bm_misstext() {
            super();
            addFrameScript(21, frame_22);
        }
        internal function frame_22():* {
            stop();
                        parent.removeChild(this);
        }
    }
}
