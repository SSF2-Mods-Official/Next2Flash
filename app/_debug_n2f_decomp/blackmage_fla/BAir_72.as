package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class BAir_72 extends MovieClip {
        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function BAir_72() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(1, frame_2);
            addFrameScript(2, frame_3);
            addFrameScript(5, frame_6);
            addFrameScript(12, frame_13);
            addFrameScript(16, frame_17);
            addFrameScript(17, frame_18);
            addFrameScript(22, frame_23);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (this.self && SSF2API.isReady())
                        {
                            this.self.setLandingLag(false);
                            this.self.attachEffect("global_spark", {
                                "x":this.self.flipX(6),
                                "y":-25
                            });
                        };
        }
        internal function frame_2():* {
            this.self.playSound("bm_knife");
                        this.self.setLandingLag(true);
                        this.self.addEffectToList(this.self.attachEffect("trail_bmage_bair", {
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true,
                            "syncHitStun":true
                        }));
                        this.self.clearEffectsOnStateChange();
        }
        internal function frame_3():* {
            this.self.attachEffect("global_dust_blast", {
                            "x":this.self.flipX(-35),
                            "y":-4,
                            "parentLock":true
                        });
        }
        internal function frame_6():* {
            this.self.updateAttackBoxStats(1, {
                            "damage":6,
                            "direction":125,
                            "hitStun":3,
                            "selfHitStun":1
                        });
        }
        internal function frame_13():* {
            this.self.setLandingLag(false);
        }
        internal function frame_17():* {
            this.self.endAttack();
        }
        internal function frame_18():* {
            this.self.updateAttackStats({"cancelWhenAirborne":true});
                        this.self.removeAllEffects();
                        SSF2API.getCamera().shake(2);
                        if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_land_s");
                        }
                        else
                        {
                            this.self.playSound("blackmage_landLight");
                        };
        }
        internal function frame_23():* {
            this.self.endAttack();
        }
    }
}
