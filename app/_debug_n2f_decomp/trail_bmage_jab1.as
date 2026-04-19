package {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class trail_bmage_jab1 extends MovieClip {
        public function trail_bmage_jab1() {
            super();
            addFrameScript(5, frame_6);
        }
        internal function frame_6():* {
            stop();
                        if (parent)
                        {
                            parent.removeChild(this);
                        };
        }
    }
}
