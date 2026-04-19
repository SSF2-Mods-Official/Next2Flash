package {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class blackmage_uspec_endb extends MovieClip {
        public function blackmage_uspec_endb() {
            super();
            addFrameScript(11, frame_12);
        }
        internal function frame_12():* {
            stop();
                        if (parent)
                        {
                            parent.removeChild(this);
                        };
        }
    }
}
