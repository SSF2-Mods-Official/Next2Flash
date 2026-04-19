package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Get_Up_127 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var ready:*;
        public function Get_Up_127() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(12, frame_13);
            addFrameScript(14, frame_15);
            addFrameScript(15, frame_16);
            addFrameScript(26, frame_27);
            addFrameScript(30, frame_31);
            addFrameScript(35, frame_36);
            addFrameScript(36, frame_37);
            addFrameScript(46, frame_47);
            addFrameScript(49, frame_50);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var ready:*;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        this.ready = false;
                        if (parent && SSF2API.isReady() && this.self)
                        {
                            SSF2API.getCamera().shake(3);
                            if (this.self.getMetalStatus())
                            {
                                this.self.playSound("metal_land_m");
                            }
                            else
                            {
                                this.self.playSound("blackmage_landHeavy");
                            };
                        };
        }
        internal function frame_13():* {
            this.self.attachEffect("effect_land");
                        this.ready = true;
                        SSF2API.getCamera().shake(2);
                        if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_land_m");
                        }
                        else
                        {
                            this.self.playSound("blackmage_landLight");
                        };
        }
        internal function frame_15():* {
            this.self.stancePlayFrame("dead");
        }
        internal function frame_16():* {
            if (!this.self.isForcedCrash())
                        {
                            this.self.setIntangibility(true);
                        };
        }
        internal function frame_27():* {
            this.self.setIntangibility(false);
        }
        internal function frame_31():* {
            this.self.endAttack();
        }
        internal function frame_36():* {
            if (this.self.getGlobalVariable("standloop") > 0)
                        {
                            gotoAndStop("standloop");
                        };
        }
        internal function frame_37():* {
            if (this.self.getGlobalVariable("standtime") > 0)
                        {
                            gotoAndStop("standloop");
                            this.self.createTimer(1, -1, this.standCountdown);
                        };
        }
        internal function frame_47():* {
            this.self.attachEffect("effect_land");
                        SSF2API.getCamera().shake(2);
                        if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_land_m");
                        }
                        else
                        {
                            this.self.playSound("blackmage_landLight");
                        };
        }
        internal function frame_50():* {
            if (this.self.getState() == CState.CRASH_GETUP)
                        {
                            this.self.setState(CState.CRASH_LAND);
                        };
                        gotoAndStop("dead");
        }
    }
}
