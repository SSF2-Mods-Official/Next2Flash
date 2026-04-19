package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class FThrow_77 extends MovieClip {
        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:BlackMageExt;
        public function FThrow_77() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(15, frame_16);
            addFrameScript(16, frame_17);
            addFrameScript(25, frame_26);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var attackBox2:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var touchBox:MovieClip;
            var self:BlackMageExt;
            if (SSF2API.isReady())
                        {
                            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        };
                        if (parent && SSF2API.isReady())
                        {
                            this.self.playSound("bm_Aero_start1");
                            this.self.playSound("bm_Aero_start2");
                        };
        }
        internal function frame_3():* {
            this.self.fireProjectile("bm_fthrowProj");
        }
        internal function frame_16():* {
            this.self.updateAttackStats({"refreshRate":50});
                        this.self.updateAttackBoxStats(2, {
                            "damage":3,
                            "direction":25,
                            "selfHitStun":1,
                            "hasEffect":true
                        });
                        this.self.refreshAttackID();
        }
        internal function frame_17():* {
            if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_step_s1");
                        }
                        else
                        {
                            this.self.playSound("bm_footstep");
                        };
        }
        internal function frame_26():* {
            this.self.endAttack();
        }
    }
}
