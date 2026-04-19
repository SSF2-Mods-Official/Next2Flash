package {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class blackmage_dsmash_ice extends MovieClip {
        public function blackmage_dsmash_ice() {
            super();
            addFrameScript(16, frame_17);
        }
        internal function frame_17():* {
            stop();
                        if (parent)
                        {
                            parent.removeChild(this);
                        };
        }
    }
}
