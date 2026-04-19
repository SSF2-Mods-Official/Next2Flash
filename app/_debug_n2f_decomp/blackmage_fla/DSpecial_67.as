package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class DSpecial_67 extends MovieClip {
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
        public var prepIt:*;
        public var doIt:Boolean;
        public var projectile:*;
        public var killProj:*;
        public function DSpecial_67() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(4, frame_5);
            addFrameScript(10, frame_11);
            addFrameScript(11, frame_12);
            addFrameScript(14, frame_15);
            addFrameScript(15, frame_16);
            addFrameScript(25, frame_26);
            addFrameScript(27, frame_28);
            addFrameScript(33, frame_34);
            addFrameScript(53, frame_54);
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
            var prepIt:*;
            var doIt:Boolean;
            var projectile:*;
            var killProj:*;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        this.MENAH = 5;
                        if (this.self && SSF2API.isReady())
                        {
                            this.controls = this.self.getControls();
                            this.maxCharge = this.self.getAttackStat("chargetime_max");
                            this.curCharge = this.self.getGlobalVariable("BMageDSpecCharge");
                            this.curFrame = this.self.getGlobalVariable("BMageDSpecFrame");
                            this.prepIt = false;
                            this.doIt = this.self.getGlobalVariable("BMageDSpecDoIt");
                            this.projectile = this.self.getGlobalVariable("BMageDSpecProj");
                            this.killProj = false;
                            this.self.createTimer(1, -1, this.checkSpeckill, {"persistent":true});
                            if (this.projExists())
                            {
                                if (this.doIt)
                                {
                                    this.self.stancePlayFrame("attack");
                                }
                                else
                                {
                                    this.self.stancePlayFrame("charging");
                                };
                            }
                            else
                            {
                                this.curCharge = 0;
                                this.doIt = false;
                                if (this.curFrame > 0)
                                {
                                    if (this.curFrame > 3)
                                    {
                                        SSF2API.print("HUH");
                                        this.curFrame = 3;
                                    };
                                    this.self.stancePlayFrame((currentFrame + this.curFrame));
                                }
                                else
                                {
                                    this.self.playSound("bm_FS_spellcast");
                                };
                            };
                        };
        }
        internal function frame_5():* {
            this.projectile = this.self.fireProjectile("meteor");
                        this.self.setGlobalVariable("BMageDSpecProj", this.projectile);
                        this.projectile.addToCamera();
                        this.self.attachEffect("global_spark", {"x":this.self.flipX(18)});
                        SSF2API.getCamera().shake(3);
                        this.curFrame = 0;
        }
        internal function frame_11():* {
            this.controls = this.self.getControls();
                        if (!this.controls.BUTTON1)
                        {
                            this.self.createTimer(1, -1, this.checkProjectile);
                            this.self.stancePlayFrame("attack");
                        };
        }
        internal function frame_12():* {
            if (!this.prepIt)
                        {
                            this.prepIt = true;
                            this.self.createTimer(1, -1, this.checkFire);
                            this.self.createTimer(1, -1, this.checkProjectile);
                            if (this.curFrame > 0)
                            {
                                if (this.curFrame > 2)
                                {
                                    SSF2API.print("OH MAN WHAT YOU DO");
                                    this.curFrame = 2;
                                };
                                this.self.stancePlayFrame((currentFrame + this.curFrame));
                            };
                        };
        }
        internal function frame_15():* {
            this.self.stancePlayFrame("charging");
        }
        internal function frame_16():* {
            if (this.projExists())
                        {
                            this.killProj = true;
                            if (this.doIt)
                            {
                                if (this.curFrame > 9)
                                {
                                    SSF2API.print("OH MAN WHAT YOU DO AGAIN");
                                    this.curFrame = 9;
                                };
                                this.self.stancePlayFrame(((currentFrame + this.curFrame) + 2));
                            }
                            else
                            {
                                this.projectile.setYSpeed(0);
                            };
                        };
        }
        internal function frame_26():* {
            this.self.attachEffect("global_sparkle", {
                            "x":this.self.flipX(15),
                            "y":-30
                        });
        }
        internal function frame_28():* {
            if (this.projExists())
                        {
                            this.killProj = false;
                            this.self.destroyTimer(this.checkProjectile);
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
        internal function frame_34():* {
            this.self.endAttack();
        }
        internal function frame_54():* {
            this.self.endAttack();
        }
    }
}
