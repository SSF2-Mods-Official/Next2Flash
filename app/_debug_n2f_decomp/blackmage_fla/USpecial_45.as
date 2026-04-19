package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class USpecial_45 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var xframe:String;
        public var projectile:*;
        public var targetProjectile:*;
        public function USpecial_45() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(1, frame_2);
            addFrameScript(5, frame_6);
            addFrameScript(6, frame_7);
            addFrameScript(7, frame_8);
            addFrameScript(22, frame_23);
            addFrameScript(23, frame_24);
            addFrameScript(24, frame_25);
            addFrameScript(25, frame_26);
            addFrameScript(33, frame_34);
            addFrameScript(37, frame_38);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var xframe:String;
            var projectile:*;
            var targetProjectile:*;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (this.self && SSF2API.isReady())
                        {
                            this.xframe = null;
                            this.self.playSound("bm_Warp_part1");
                            this.projectile = null;
                            if (this.self.isCPU() && !(this.self.isOnGround()))
                            {
                                if (this.self.inLowerLeftWarningBounds())
                                {
                                    this.self.importCPUControls([6465, 56]);
                                }
                                else if (this.self.inLowerRightWarningBounds())
                                {
                                    this.self.importCPUControls([6721, 53]);
                                };
                            };
                            this.self.attachEffect("global_sparkle", {
                                "x":this.self.flipX(15),
                                "y":-20
                            });
                        };
        }
        internal function frame_2():* {
            this.self.pushEffectBehind(this.self.addEffectToList(this.self.attachEffect("blackmage_uspec_start", {
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true
                        })));
                        this.self.clearEffectsOnStateChange(false);
        }
        internal function frame_6():* {
            this.projectile = this.self.fireProjectile("warp");
                        this.targetProjectile = this.projectile;
                        this.projectile.addToCamera();
                        this.self.addEventListener(SSF2Event.CHAR_HURT, this.removeProjectile, {"persistent":true});
                        this.self.addEventListener(SSF2Event.CHAR_KO_DEATH, this.removeProjectile);
                        this.self.addEventListener(SSF2Event.STATE_CHANGE, this.removeProjectile);
        }
        internal function frame_7():* {
            this.xframe = "charging";
                        if (this.self.getCurrentProjectile() != null)
                        {
                            this.self.getCurrentProjectile().updateProjectileStats({"controlDirection":90});
                        };
        }
        internal function frame_8():* {
            if (this.self.getCurrentProjectile() != null)
                        {
                            this.self.getCurrentProjectile().endControl();
                        };
        }
        internal function frame_23():* {
            this.self.stancePlayFrame("charging");
        }
        internal function frame_24():* {
            this.xframe = "attack";
                        this.self.playSound("bm_Warp_part2");
                        this.self.removeAllEffects();
                        this.self.pushEffectBehind(this.self.addEffectToList(this.self.attachEffect("blackmage_uspec_endb", {
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true
                        })));
                        this.self.addEffectToList(this.self.attachEffect("blackmage_uspec_endf", {
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true
                        }));
                        if (this.self.getCurrentProjectile() != null)
                        {
                            this.projectile.endControl();
                        };
        }
        internal function frame_25():* {
            if (this.self.getCurrentProjectile() != null)
                        {
                            this.projectile.getStanceMC().self.stancePlayFrame("continue");
                        };
        }
        internal function frame_26():* {
            this.self.updateAttackStats({"air_ease":0});
                        this.self.unnattachFromGround();
                        if (this.self.getCurrentProjectile() != null)
                        {
                            this.projectile.setXSpeed(0);
                            this.projectile.setYSpeed(0);
                        };
        }
        internal function frame_34():* {
            if (this.self.getCurrentProjectile() != null)
                        {
                            if (!SSF2API.hitTestGround(this.projectile.getMC().x, (this.projectile.getMC().y - this.self.getCharacterStat("height"))) || !(this.projectile.isOnGround()))
                            {
                                parent.x = this.projectile.getMC().x;
                                parent.y = this.projectile.getMC().y;
                            };
                        };
                        this.self.attachEffect("global_dust_swirl");
                        this.self.removeEventListener(SSF2Event.CHAR_HURT, this.removeProjectile);
                        this.self.removeEventListener(SSF2Event.CHAR_KO_DEATH, this.removeProjectile);
                        this.self.removeEventListener(SSF2Event.STATE_CHANGE, this.removeProjectile);
        }
        internal function frame_38():* {
            this.self.toHelpless();
        }
    }
}
