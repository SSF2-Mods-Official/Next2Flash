package {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class blackmage_demieffect extends MovieClip {
        public function blackmage_demieffect() {
            super();
            addFrameScript(17, frame_18);
        }
        internal function frame_18():* {
            stop();
                        if (parent != null)
                        {
                            parent.removeChild(this);
                        };
        }
    }
}
