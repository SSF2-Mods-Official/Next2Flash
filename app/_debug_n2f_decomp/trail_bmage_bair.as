package {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class trail_bmage_bair extends MovieClip {
        public function trail_bmage_bair() {
            super();
            addFrameScript(6, frame_7);
        }
        internal function frame_7():* {
            stop();
                        if (parent)
                        {
                            parent.removeChild(this);
                        };
        }
    }
}
