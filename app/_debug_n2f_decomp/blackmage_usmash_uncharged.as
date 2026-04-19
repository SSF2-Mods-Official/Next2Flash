package {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class blackmage_usmash_uncharged extends MovieClip {
        public function blackmage_usmash_uncharged() {
            super();
            addFrameScript(13, frame_14);
        }
        internal function frame_14():* {
            stop();
                        if (parent)
                        {
                            parent.removeChild(this);
                        };
        }
    }
}
