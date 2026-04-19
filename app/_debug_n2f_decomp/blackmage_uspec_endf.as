package {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class blackmage_uspec_endf extends MovieClip {
        public function blackmage_uspec_endf() {
            super();
            addFrameScript(15, frame_16);
        }
        internal function frame_16():* {
            stop();
                        if (parent)
                        {
                            parent.removeChild(this);
                        };
        }
    }
}
