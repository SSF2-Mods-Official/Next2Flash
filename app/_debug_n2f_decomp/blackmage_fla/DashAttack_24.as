package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class DashAttack_24 extends MovieClip {
        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function DashAttack_24() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(1, frame_2);
            addFrameScript(3, frame_4);
            addFrameScript(5, frame_6);
            addFrameScript(7, frame_8);
            addFrameScript(8, frame_9);
            addFrameScript(10, frame_11);
            addFrameScript(12, frame_13);
            addFrameScript(18, frame_19);
            addFrameScript(23, frame_24);
            addFrameScript(30, frame_31);
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
        }
        internal function frame_2():* {
            this.self.playAttackSound(1);
        }
        internal function frame_4():* {
            this.self.setXSpeed(0);
                        this.self.addEffectToList(this.self.attachEffect("blackmage_dash_attack", {
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true,
                            "syncHitStun":true
                        }));
                        this.self.clearEffectsOnStateChange();
                        this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(-5),
                            "y":-30
                        });
        }
        internal function frame_6():* {
            this.self.updateAttackStats({"superArmor":true});
        }
        internal function frame_8():* {
            this.self.attachEffect("global_dust_light");
        }
        internal function frame_9():* {
            this.self.setXSpeed(8, false);
                        this.self.playAttackSound(2);
        }
        internal function frame_11():* {
            SSF2API.getCamera().shake(5);
                        this.self.playSound("bm_bthrow_hit");
                        this.self.attachEffect("ground_bounce");
                        this.self.attachEffect("global_dust_cloud");
                        if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_land_l");
                        };
        }
        internal function frame_13():* {
            this.self.updateAttackBoxStats(1, {
                            "damage":8,
                            "direction":30,
                            "kbConstant":60,
                            "hitStun":1,
                            "selfHitStun":1
                        });
        }
        internal function frame_19():* {
            this.self.updateAttackStats({"superArmor":false});
        }
        internal function frame_24():* {
            this.self.setXSpeed(0);
        }
        internal function frame_31():* {
            this.self.endAttack();
        }
    }
}
