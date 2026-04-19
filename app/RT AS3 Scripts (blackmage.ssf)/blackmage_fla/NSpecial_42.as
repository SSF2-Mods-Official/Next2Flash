// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.NSpecial_42

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class NSpecial_42 extends MovieClip 
    {

        internal var attackBox:MovieClip;
        internal var attackBox2:MovieClip;
        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var reverseBox:MovieClip;
        internal var reverseBox2:MovieClip;
        internal var self:BlackMageExt;
        internal var controls:Object;
        internal var curCharge:int;
        internal var wasFacingLeft:Boolean;
        internal var delaySpecKill:Boolean;

        public function NSpecial_42()
        {
            addFrameScript(0, this.frame1, 4, this.frame5, 20, this.frame21, 24, this.frame25, 28, this.frame29, 36, this.frame37, 40, this.frame41, 44, this.frame45, 52, this.frame53, 56, this.frame57, 60, this.frame61, 68, this.frame69, 72, this.frame73, 76, this.frame77, 84, this.frame85, 88, this.frame89, 92, this.frame93, 101, this.frame102, 102, this.frame103, 103, this.frame104, 108, this.frame109, 114, this.frame115, 118, this.frame119, 124, this.frame125, 127, this.frame128);
        }

        public function reflected(_arg_1:*=null):*
        {
            this.self.playSound("reflect_sfx");
            SSF2API.attachEffect("reflect_effect", {
                "x":_arg_1.data.opponent.getX(),
                "y":_arg_1.data.opponent.getY()
            });
        }

        public function checkRelease():void
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON1)
            {
                this.self.destroyTimer(this.checkRelease);
                this.stopSFX();
                this.self.stancePlayFrame("attack");
            };
        }

        public function checkShield():void
        {
            this.controls = this.self.getControls();
            if (this.controls.SHIELD)
            {
                if (this.wasFacingLeft)
                {
                    this.self.faceLeft();
                };
                this.self.destroyTimer(this.checkRelease);
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("BMageNSpecCharge", this.curCharge);
                this.stopSFX();
                this.self.endAttack();
            };
        }

        public function checkSpeckill():void
        {
            if (!this.self.inState(CState.ATTACKING))
            {
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("BMageNSpecCharge", 0);
                this.stopSFX();
            };
        }

        public function checkStopSFX():void
        {
            if (!this.self.inState(CState.ATTACKING))
            {
                this.self.destroyTimer(this.checkStopSFX);
                this.stopSFX();
            };
        }

        public function stopSFX():void
        {
            var _local_1:* = this.self.getGlobalVariable("BMageNSpecSFX");
            if (_local_1 != null)
            {
                SSF2API.stopSound(_local_1);
                this.self.setGlobalVariable("BMageNSpecSFX", null);
            };
        }

        public function stunProjectile(_arg_1:*):void
        {
            this.curCharge = _arg_1.data.caller.getGlobalVariable("BMageNSpecCharge");
            if (this.curCharge < 1)
            {
                this.curCharge = 1;
            };
            this.self.playAttackSound(4);
            _arg_1.data.opponent.forceHitStun((15 * this.curCharge));
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:MovieClip;
            var _local_6:MovieClip;
            var _local_7:MovieClip;
            var _local_8:MovieClip;
            var _local_9:BlackMageExt;
            var _local_10:Object;
            var _local_11:int;
            var _local_12:Boolean;
            var _local_13:Boolean;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if ((((parent) && (SSF2API.isReady())) && (this.self)))
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

        internal function frame5():*
        {
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

        internal function frame21():*
        {
            this.self.playAttackSound(2);
            this.curCharge = 1;
        }

        internal function frame25():*
        {
            this.checkShield();
        }

        internal function frame29():*
        {
            this.checkShield();
        }

        internal function frame37():*
        {
            this.self.playAttackSound(2);
            this.curCharge = 2;
        }

        internal function frame41():*
        {
            this.checkShield();
        }

        internal function frame45():*
        {
            this.checkShield();
        }

        internal function frame53():*
        {
            this.self.playAttackSound(2);
            this.curCharge = 3;
        }

        internal function frame57():*
        {
            this.checkShield();
        }

        internal function frame61():*
        {
            this.checkShield();
        }

        internal function frame69():*
        {
            this.self.playAttackSound(2);
            this.curCharge = 4;
        }

        internal function frame73():*
        {
            this.checkShield();
        }

        internal function frame77():*
        {
            this.checkShield();
        }

        internal function frame85():*
        {
            this.self.playAttackSound(2);
            this.curCharge = 5;
        }

        internal function frame89():*
        {
            this.checkShield();
        }

        internal function frame93():*
        {
            this.checkShield();
        }

        internal function frame102():*
        {
            this.self.playAttackSound(2);
            this.curCharge = 6;
        }

        internal function frame103():*
        {
            this.checkShield();
            this.stopSFX();
        }

        internal function frame104():*
        {
            this.self.destroyTimer(this.checkRelease);
            this.self.setGlobalVariable("BMageNSpecCharge", this.curCharge);
            if (this.curCharge < 1)
            {
                this.curCharge = 1;
            };
            this.self.playAttackSound(3);
            this.self.updateAttackBoxStats(1, {"hitStun":(15 * this.curCharge)});
            this.self.updateAttackBoxStats(2, {"hitStun":(15 * this.curCharge)});
            if (((this.self.isCPU()) && (this.curCharge >= 3)))
            {
                this.self.setCPUAttackQueue("a_forwardsmash,a_up");
            };
        }

        internal function frame109():*
        {
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

        internal function frame115():*
        {
            this.self.addEventListener(SSF2Event.REVERSE_HIT, this.stunProjectile);
            SSF2API.getCamera().shake(4);
        }

        internal function frame119():*
        {
            this.self.removeEventListener(SSF2Event.REVERSE_HIT, this.stunProjectile);
        }

        internal function frame125():*
        {
            if (this.wasFacingLeft)
            {
                this.self.faceLeft();
            };
        }

        internal function frame128():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

