package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Revival_8 extends MovieClip {
        public var self:BlackMageExt;
        public function Revival_8() {
            super();
            addFrameScript(0, frame_1);
        }
        internal function frame_1():* {
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (SSF2API.isReady())
                        {
                            this.self.setGlobalVariable("canStartRise", true);
                        };
        }
    }
}
