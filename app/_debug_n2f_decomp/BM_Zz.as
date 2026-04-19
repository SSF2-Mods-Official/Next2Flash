package {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class BM_Zz extends MovieClip {
        public function BM_Zz() {
            super();
            addFrameScript(27, frame_28);
        }
        internal function frame_28():* {
            stop();
                        parent.removeChild(this);
        }
    }
}
