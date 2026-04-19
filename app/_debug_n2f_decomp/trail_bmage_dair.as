package {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class trail_bmage_dair extends MovieClip {
        public function trail_bmage_dair() {
            super();
            addFrameScript(8, frame_9);
        }
        internal function frame_9():* {
            stop();
                        if (parent)
                        {
                            parent.removeChild(this);
                        };
        }
    }
}
