package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Stunned_120 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function Stunned_120() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(25, frame_26);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (parent && SSF2API.isReady())
                        {
                            this.self.playSound("bm_Dizzy");
                            this.self.setGlobalVariable("jab", false);
                        };
        }
        internal function frame_26():* {
            this.self.stancePlayFrame("again");
        }
    }
}
