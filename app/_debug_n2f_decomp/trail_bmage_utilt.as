package {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class trail_bmage_utilt extends MovieClip {
        public function trail_bmage_utilt() {
            super();
            addFrameScript(7, frame_8);
        }
        internal function frame_8():* {
            stop();
                        if (parent)
                        {
                            parent.removeChild(this);
                        };
        }
    }
}
