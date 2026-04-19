package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class NSpecial_42 extends MovieClip {
        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var reverseBox:MovieClip;
        public var reverseBox2:MovieClip;
        public var self:BlackMageExt;
        public var controls:Object;
        public var curCharge:int;
        public var wasFacingLeft:Boolean;
        public var delaySpecKill:Boolean;
        public var _local_1:* = this.self.getGlobalVariable("BMageNSpecSFX");
        public function NSpecial_42() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(4, frame_5);
            addFrameScript(20, frame_21);
            addFrameScript(24, frame_25);
            addFrameScript(28, frame_29);
            addFrameScript(36, frame_37);
            addFrameScript(40, frame_41);
            addFrameScript(44, frame_45);
            addFrameScript(52, frame_53);
            addFrameScript(56, frame_57);
            addFrameScript(60, frame_61);
            addFrameScript(68, frame_69);
            addFrameScript(72, frame_73);
            addFrameScript(76, frame_77);
            addFrameScript(84, frame_85);
            addFrameScript(88, frame_89);
            addFrameScript(92, frame_93);
            addFrameScript(101, frame_102);
            addFrameScript(102, frame_103);
            addFrameScript(103, frame_104);
            addFrameScript(108, frame_109);
            addFrameScript(114, frame_115);
            addFrameScript(118, frame_119);
            addFrameScript(124, frame_125);
            addFrameScript(127, frame_128);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var attackBox2:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var reverseBox:MovieClip;
            var reverseBox2:MovieClip;
            var self:BlackMageExt;
            var controls:Object;
            var curCharge:int;
            var wasFacingLeft:Boolean;
            var delaySpecKill:Boolean;
            var _local_1:* = this.self.getGlobalVariable("BMageNSpecSFX");
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (parent && SSF2API.isReady() && this.self)
                        {
                            this.controls = this.self.getControls();
                            this.curCharge = this.self.getGlobalVariable("BMageNSpecCharge");
                            this.wasFacingLeft = false;
                            this.delaySpecKill = true;
                            if (this.curCharge < 1)
                            {
                                this.delaySpecKill = false;
                                this.self.createTimer(1, -1, this.checkSpeckill, {"persistent":true});
                            }
                            else
                            {
                                this.self.createTimer(1, -1, this.checkStopSFX, {"persistent":true});
                            };
                            this.self.setGlobalVariable("BMageNSpecSFX", this.self.playAttackSound(1));
                            this.self.attachEffect("global_sparkle", {
                                "x":this.self.flipX(-15),
                                "y":-20
                            });
                            this.self.addEventListener(SSF2Event.REVERSE_HIT, this.reflected);
                        };
        }
        internal function frame_5():* {
            if (!this.self.isFacingRight())
                        {
                            this.self.faceRight();
                            this.wasFacingLeft = true;
                        };
                        if (this.curCharge >= 1)
                        {
                            this.self.destroyTimer(this.checkStopSFX);
                            this.stopSFX();
                            this.self.stancePlayFrame("attack");
                        }
                        else
                        {
                            this.self.createTimer(1, -1, this.checkRelease);
                        };
        }
        internal function frame_21():* {
            this.self.playAttackSound(2);
                        this.curCharge = 1;
        }
        internal function frame_25():* {
            this.checkShield();
        }
        internal function frame_29():* {
            this.checkShield();
        }
        internal function frame_37():* {
            this.self.playAttackSound(2);
                        this.curCharge = 2;
        }
        internal function frame_41():* {
            this.checkShield();
        }
        internal function frame_45():* {
            this.checkShield();
        }
        internal function frame_53():* {
            this.self.playAttackSound(2);
                        this.curCharge = 3;
        }
        internal function frame_57():* {
            this.checkShield();
        }
        internal function frame_61():* {
            this.checkShield();
        }
        internal function frame_69():* {
            this.self.playAttackSound(2);
                        this.curCharge = 4;
        }
        internal function frame_73():* {
            this.checkShield();
        }
        internal function frame_77():* {
            this.checkShield();
        }
        internal function frame_85():* {
            this.self.playAttackSound(2);
                        this.curCharge = 5;
        }
        internal function frame_89():* {
            this.checkShield();
        }
        internal function frame_93():* {
            this.checkShield();
        }
        internal function frame_102():* {
            this.self.playAttackSound(2);
                        this.curCharge = 6;
        }
        internal function frame_103():* {
            this.checkShield();
                        this.stopSFX();
        }
        internal function frame_104():* {
            this.self.destroyTimer(this.checkRelease);
                        this.self.setGlobalVariable("BMageNSpecCharge", this.curCharge);
                        if (this.curCharge < 1)
                        {
                            this.curCharge = 1;
                        };
                        this.self.playAttackSound(3);
                        this.self.updateAttackBoxStats(1, {"hitStun":(15 * this.curCharge)});
                        this.self.updateAttackBoxStats(2, {"hitStun":(15 * this.curCharge)});
                        if (this.self.isCPU() && (this.curCharge >= 3))
                        {
                            this.self.setCPUAttackQueue("a_forwardsmash,a_up");
                        };
        }
        internal function frame_109():* {
            if (this.delaySpecKill)
                        {
                            this.self.createTimer(1, -1, this.checkSpeckill, {"persistent":true});
                        };
                        this.self.attachEffect("global_dust_swirl");
                        if (this.self.specialEvent)
                        {
                            this.self.updateAttackBoxStats(1, {"hitStun":9999999});
                        };
        }
        internal function frame_115():* {
            this.self.addEventListener(SSF2Event.REVERSE_HIT, this.stunProjectile);
                        SSF2API.getCamera().shake(4);
        }
        internal function frame_119():* {
            this.self.removeEventListener(SSF2Event.REVERSE_HIT, this.stunProjectile);
        }
        internal function frame_125():* {
            if (this.wasFacingLeft)
                        {
                            this.self.faceLeft();
                        };
        }
        internal function frame_128():* {
            this.self.endAttack();
        }
    }
}
