package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Get_UpRoll_128 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function Get_UpRoll_128() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(10, frame_11);
            addFrameScript(17, frame_18);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            if (SSF2API.isReady())
                        {
                            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        };
                        if (parent && SSF2API.isReady())
                        {
                            this.self.setIntangibility(true);
                        };
        }
        internal function frame_11():* {
            this.self.setIntangibility(false);
        }
        internal function frame_18():* {
            this.self.endAttack();
        }
    }
}
