package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class DAir_73 extends MovieClip {
        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function DAir_73() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(4, frame_5);
            addFrameScript(6, frame_7);
            addFrameScript(8, frame_9);
            addFrameScript(9, frame_10);
            addFrameScript(10, frame_11);
            addFrameScript(11, frame_12);
            addFrameScript(17, frame_18);
            addFrameScript(20, frame_21);
            addFrameScript(21, frame_22);
            addFrameScript(33, frame_34);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var attackBox2:MovieClip;
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
        internal function frame_5():* {
            this.self.setLandingLag(true);
                        this.self.playSound("bm_scythe");
        }
        internal function frame_7():* {
            this.self.addEffectToList(this.self.attachEffect("trail_bmage_dair", {
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true,
                            "syncHitStun":true
                        }));
                        this.self.clearEffectsOnStateChange();
        }
        internal function frame_9():* {
            this.self.updateAttackBoxStats(1, {
                            "damage":10,
                            "kbConstant":95,
                            "effectSound":"sw_strongslash"
                        });
        }
        internal function frame_10():* {
            this.self.updateAttackBoxStats(1, {
                            "damage":8,
                            "direction":200,
                            "kbConstant":80,
                            "effectSound":"sw_slash"
                        });
        }
        internal function frame_11():* {
            this.self.updateAttackBoxStats(2, {"direction":200});
                        if (!(this.self.deathProj) || this.self.deathProj.isDisposed())
                        {
                            this.self.deathProj = this.self.fireProjectile("death", this.self.flipX(this.self.getXSpeed()), this.self.getYSpeed());
                            this.self.attachEffect("global_spark", {
                                "x":(this.self.flipX(-9) + this.self.getXSpeed()),
                                "y":(14 + this.self.getYSpeed())
                            });
                        };
        }
        internal function frame_12():* {
            this.self.updateAttackBoxStats(1, {
                            "direction":150,
                            "kbConstant":60
                        });
                        this.self.updateAttackBoxStats(2, {
                            "direction":150,
                            "kbConstant":60
                        });
        }
        internal function frame_18():* {
            this.self.setLandingLag(false);
        }
        internal function frame_21():* {
            this.self.endAttack();
        }
        internal function frame_22():* {
            this.self.updateAttackStats({
                            "cancelWhenAirborne":true,
                            "allowControl":false
                        });
                        this.self.removeAllEffects();
                        SSF2API.getCamera().shake(4);
                        if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_land_l");
                        }
                        else
                        {
                            this.self.playSound("blackmage_landHeavy");
                        };
        }
        internal function frame_34():* {
            this.self.endAttack();
        }
    }
}
