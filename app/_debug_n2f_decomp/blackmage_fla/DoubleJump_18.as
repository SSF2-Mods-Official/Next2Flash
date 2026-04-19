package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class DoubleJump_18 extends MovieClip {
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var done:Boolean;
        public var xframe:*;
        public function DoubleJump_18() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(7, frame_8);
            addFrameScript(15, frame_16);
        }
        internal function frame_1():* {
            var hand:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var done:Boolean;
            var xframe:*;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (SSF2API.isReady() && this.self)
                        {
                            this.done = false;
                            this.xframe = "midair";
                            if (this.self.getGlobalVariable("screwAttackOn") && (this.self.getMidairJumpCount() < 2))
                            {
                                this.self.forceAttack("item_screw");
                            }
                            else if (this.self.getGlobalVariable("sonicShieldFiredash") && (this.self.getControls().LEFT || this.self.getControls().RIGHT))
                            {
                                this.self.forceAttack("item_firedash");
                            }
                            else if (this.self.getGlobalVariable("sonicShieldBubbleBounce") && this.self.getControls().DOWN)
                            {
                                this.self.forceAttack("item_bubblebounce");
                            }
                            else if ((this.self.isFacingRight() && this.self.getControls().LEFT) || (!(this.self.isFacingRight()) && this.self.getControls().RIGHT))
                            {
                                this.self.stancePlayFrame("backflip");
                            };
                        };
        }
        internal function frame_8():* {
            this.self.endAttack();
        }
        internal function frame_16():* {
            this.self.endAttack();
        }
    }
}
