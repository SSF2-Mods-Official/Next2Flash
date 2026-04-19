package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Get_UpAttack_129 extends MovieClip {
        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function Get_UpAttack_129() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(8, frame_9);
            addFrameScript(11, frame_12);
            addFrameScript(13, frame_14);
            addFrameScript(15, frame_16);
            addFrameScript(24, frame_25);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
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
        internal function frame_9():* {
            this.self.playAttackSound(1);
        }
        internal function frame_12():* {
            this.self.attachEffect("global_dust_swirl");
        }
        internal function frame_14():* {
            this.self.playAttackSound(2);
        }
        internal function frame_16():* {
            this.self.setIntangibility(false);
        }
        internal function frame_25():* {
            this.self.endAttack();
        }
    }
}
