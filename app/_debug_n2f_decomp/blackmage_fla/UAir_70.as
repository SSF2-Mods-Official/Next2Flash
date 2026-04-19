package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class UAir_70 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function UAir_70() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(4, frame_5);
            addFrameScript(6, frame_7);
            addFrameScript(8, frame_9);
            addFrameScript(12, frame_13);
            addFrameScript(15, frame_16);
            addFrameScript(16, frame_17);
            addFrameScript(22, frame_23);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (this.self && SSF2API.isReady())
                        {
                            this.self.setLandingLag(false);
                        };
        }
        internal function frame_3():* {
            this.self.fireProjectile("waterspout_strong");
                        this.self.setLandingLag(true);
                        this.self.playAttackSound(1);
        }
        internal function frame_5():* {
            this.self.fireProjectile("waterspout");
        }
        internal function frame_7():* {
            this.self.fireProjectile("waterspout");
        }
        internal function frame_9():* {
            this.self.fireProjectile("waterspout_strong");
        }
        internal function frame_13():* {
            this.self.setLandingLag(false);
        }
        internal function frame_16():* {
            this.self.endAttack();
        }
        internal function frame_17():* {
            SSF2API.getCamera().shake(2);
                        if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_land_m");
                        }
                        else
                        {
                            this.self.playSound("blackmage_landHeavy");
                        };
        }
        internal function frame_23():* {
            this.self.endAttack();
        }
    }
}
