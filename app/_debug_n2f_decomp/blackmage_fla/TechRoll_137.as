package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class TechRoll_137 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function TechRoll_137() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(10, frame_11);
            addFrameScript(20, frame_21);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (SSF2API.isReady() && this.self)
                        {
                            this.self.setIntangibility(true);
                            this.self.setGlobalVariable("canStartRise", true);
                            if (!this.self.getMetalStatus())
                            {
                                this.self.playSound("menumove", true);
                            };
                        };
        }
        internal function frame_11():* {
            this.self.setIntangibility(false);
        }
        internal function frame_21():* {
            this.self.endAttack();
        }
    }
}
