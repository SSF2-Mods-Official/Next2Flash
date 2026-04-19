package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class DSpecialAir_68 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var MENAH:int;
        public var controls:Object;
        public var maxCharge:*;
        public var curCharge:int;
        public var curFrame:int;
        public var prepIt:Boolean;
        public var doIt:Boolean;
        public var projectile:*;
        public var killProj:Boolean;
        public function DSpecialAir_68() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(1, frame_2);
            addFrameScript(2, frame_3);
            addFrameScript(3, frame_4);
            addFrameScript(4, frame_5);
            addFrameScript(5, frame_6);
            addFrameScript(6, frame_7);
            addFrameScript(7, frame_8);
            addFrameScript(8, frame_9);
            addFrameScript(9, frame_10);
            addFrameScript(10, frame_11);
            addFrameScript(11, frame_12);
            addFrameScript(12, frame_13);
            addFrameScript(13, frame_14);
            addFrameScript(14, frame_15);
            addFrameScript(15, frame_16);
            addFrameScript(16, frame_17);
            addFrameScript(17, frame_18);
            addFrameScript(18, frame_19);
            addFrameScript(19, frame_20);
            addFrameScript(30, frame_31);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var MENAH:int;
            var controls:Object;
            var maxCharge:*;
            var curCharge:int;
            var curFrame:int;
            var prepIt:Boolean;
            var doIt:Boolean;
            var projectile:*;
            var killProj:Boolean;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        this.MENAH = 5;
                        if (this.self && SSF2API.isReady())
                        {
                            this.controls = this.self.getControls();
                            this.maxCharge = this.self.getAttackStat("chargetime_max");
                            this.curCharge = 0;
                            this.curFrame = 1;
                            this.prepIt = false;
                            this.doIt = false;
                            this.projectile = null;
                            this.killProj = false;
                            this.self.createTimer(1, -1, this.checkSpeckill, {"persistent":true});
                            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
                            this.self.playSound("bm_FS_spellcast");
                        };
        }
        internal function frame_2():* {
            this.curFrame = 1;
        }
        internal function frame_3():* {
            this.curFrame = 2;
        }
        internal function frame_4():* {
            this.curFrame = 3;
        }
        internal function frame_5():* {
            this.projectile = this.self.fireProjectile("meteor");
                        this.self.setGlobalVariable("BMageDSpecProj", this.projectile);
                        this.projectile.addToCamera();
                        this.self.attachEffect("global_spark", {
                            "x":this.self.flipX(18),
                            "y":-5
                        });
                        SSF2API.getCamera().shake(3);
                        this.controls = this.self.getControls();
                        if (!this.controls.BUTTON1)
                        {
                            this.self.createTimer(1, -1, this.checkProjectile);
                            this.self.stancePlayFrame("attack");
                        };
        }
        internal function frame_6():* {
            if (!this.prepIt)
                        {
                            this.prepIt = true;
                            this.self.createTimer(1, -1, this.checkFire);
                            this.self.createTimer(1, -1, this.checkProjectile);
                        };
                        this.curFrame = 0;
        }
        internal function frame_7():* {
            this.curFrame = 1;
        }
        internal function frame_8():* {
            this.curFrame = 2;
        }
        internal function frame_9():* {
            this.self.stancePlayFrame("charging");
        }
        internal function frame_10():* {
            this.killProj = true;
                        this.doIt = true;
                        this.curFrame = 0;
        }
        internal function frame_11():* {
            this.curFrame = 1;
        }
        internal function frame_12():* {
            this.curFrame = 2;
        }
        internal function frame_13():* {
            this.curFrame = 3;
        }
        internal function frame_14():* {
            this.self.attachEffect("global_sparkle", {
                            "x":this.self.flipX(15),
                            "y":-30
                        });
                        this.curFrame = 4;
        }
        internal function frame_15():* {
            this.curFrame = 5;
        }
        internal function frame_16():* {
            this.curFrame = 6;
        }
        internal function frame_17():* {
            this.curFrame = 7;
        }
        internal function frame_18():* {
            this.curFrame = 8;
        }
        internal function frame_19():* {
            this.curFrame = 9;
        }
        internal function frame_20():* {
            if (this.projExists())
                        {
                            this.killProj = false;
                            this.self.destroyTimer(this.checkProjectile);
                            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
                            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
                            this.projectile.updateProjectileStats({"maxgravity":9});
                            this.projectile.getStanceMC().self.stancePlayFrame("burn");
                            this.projectile.removeFromCamera();
                            this.controls = this.self.getControls();
                            if (this.self.isFacingRight())
                            {
                                if (this.controls.RIGHT)
                                {
                                    this.projectile.angleControl(9, 330);
                                }
                                else if (this.controls.LEFT)
                                {
                                    this.projectile.angleControl(9, 300);
                                }
                                else
                                {
                                    this.projectile.angleControl(9, 315);
                                };
                            }
                            else
                            {
                                this.projectile.flip();
                                if (this.controls.LEFT)
                                {
                                    this.projectile.angleControl(9, 210);
                                }
                                else if (this.controls.RIGHT)
                                {
                                    this.projectile.angleControl(9, 240);
                                }
                                else
                                {
                                    this.projectile.angleControl(9, 225);
                                };
                            };
                            this.self.playSound("bmfire");
                        };
        }
        internal function frame_31():* {
            this.self.endAttack();
        }
    }
}
