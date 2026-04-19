// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.DSpecialAir_68

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class DSpecialAir_68 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;
        internal var MENAH:int;
        internal var controls:Object;
        internal var maxCharge:*;
        internal var curCharge:int;
        internal var curFrame:int;
        internal var prepIt:Boolean;
        internal var doIt:Boolean;
        internal var projectile:*;
        internal var killProj:Boolean;

        public function DSpecialAir_68()
        {
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 3, this.frame4, 4, this.frame5, 5, this.frame6, 6, this.frame7, 7, this.frame8, 8, this.frame9, 9, this.frame10, 10, this.frame11, 11, this.frame12, 12, this.frame13, 13, this.frame14, 14, this.frame15, 15, this.frame16, 16, this.frame17, 17, this.frame18, 18, this.frame19, 19, this.frame20, 30, this.frame31);
        }

        public function checkFire():void
        {
            this.controls = this.self.getControls();
            this.curCharge++;
            if (((this.projExists()) && ((this.curCharge % 3) == 0)))
            {
                this.projectile.getMC().scaleX = (this.projectile.getMC().scaleX + 0.1);
                this.projectile.getMC().scaleY = (this.projectile.getMC().scaleY + 0.1);
                this.MENAH++;
                SSF2API.print(this.MENAH.toString());
            };
            if (((!(this.controls.BUTTON1)) || (this.curCharge >= this.maxCharge)))
            {
                this.self.destroyTimer(this.checkFire);
                this.self.setGlobalVariable("BMageDSpecCharge", this.curCharge);
                this.self.stancePlayFrame("attack");
            };
        }

        public function checkProjectile():void
        {
            if (!this.projExists())
            {
                this.self.destroyTimer(this.checkFire);
                this.self.destroyTimer(this.checkProjectile);
                this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
                this.self.stancePlayFrame("broken");
            }
            else
            {
                if (this.self.isFacingRight())
                {
                    this.projectile.getMC().x = (parent.x + 14);
                }
                else
                {
                    this.projectile.getMC().x = (parent.x - 14);
                };
                this.projectile.getMC().y = (parent.y - 5);
            };
        }

        public function checkSpeckill():void
        {
            if (!this.self.inState(CState.ATTACKING))
            {
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("BMageDSpecCharge", 0);
                this.self.setGlobalVariable("BMageDSpecFrame", 0);
                this.self.setGlobalVariable("BMageDSpecDoIt", false);
                this.self.setGlobalVariable("BMageDSpecProj", null);
                if (this.projExists())
                {
                    this.projectile.removeFromCamera();
                    if (this.killProj)
                    {
                        this.projectile.destroy();
                    };
                };
            };
        }

        public function toGround(_arg_1:*):void
        {
            this.self.destroyTimer(this.checkFire);
            this.self.destroyTimer(this.checkProjectile);
            this.self.destroyTimer(this.checkSpeckill);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
            this.self.setGlobalVariable("BMageDSpecCharge", this.curCharge);
            this.self.setGlobalVariable("BMageDSpecFrame", this.curFrame);
            this.self.setGlobalVariable("BMageDSpecDoIt", this.doIt);
            this.self.setGlobalVariable("BMageDSpecProj", this.projectile);
            this.self.forceAttack("b_down", null, true);
        }

        public function projExists():Boolean
        {
            return (((!(this.projectile == null)) && (!(this.projectile.isDisposed()))) && (!(this.projectile.inState(PState.DEAD))));
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:BlackMageExt;
            var _local_6:int;
            var _local_7:Object;
            var _local_8:*;
            var _local_9:int;
            var _local_10:int;
            var _local_11:Boolean;
            var _local_12:Boolean;
            var _local_13:*;
            var _local_14:Boolean;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            this.MENAH = 5;
            if (((this.self) && (SSF2API.isReady())))
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

        internal function frame2():*
        {
            this.curFrame = 1;
        }

        internal function frame3():*
        {
            this.curFrame = 2;
        }

        internal function frame4():*
        {
            this.curFrame = 3;
        }

        internal function frame5():*
        {
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

        internal function frame6():*
        {
            if (!this.prepIt)
            {
                this.prepIt = true;
                this.self.createTimer(1, -1, this.checkFire);
                this.self.createTimer(1, -1, this.checkProjectile);
            };
            this.curFrame = 0;
        }

        internal function frame7():*
        {
            this.curFrame = 1;
        }

        internal function frame8():*
        {
            this.curFrame = 2;
        }

        internal function frame9():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame10():*
        {
            this.killProj = true;
            this.doIt = true;
            this.curFrame = 0;
        }

        internal function frame11():*
        {
            this.curFrame = 1;
        }

        internal function frame12():*
        {
            this.curFrame = 2;
        }

        internal function frame13():*
        {
            this.curFrame = 3;
        }

        internal function frame14():*
        {
            this.self.attachEffect("global_sparkle", {
                "x":this.self.flipX(15),
                "y":-30
            });
            this.curFrame = 4;
        }

        internal function frame15():*
        {
            this.curFrame = 5;
        }

        internal function frame16():*
        {
            this.curFrame = 6;
        }

        internal function frame17():*
        {
            this.curFrame = 7;
        }

        internal function frame18():*
        {
            this.curFrame = 8;
        }

        internal function frame19():*
        {
            this.curFrame = 9;
        }

        internal function frame20():*
        {
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
                    else
                    {
                        if (this.controls.LEFT)
                        {
                            this.projectile.angleControl(9, 300);
                        }
                        else
                        {
                            this.projectile.angleControl(9, 315);
                        };
                    };
                }
                else
                {
                    this.projectile.flip();
                    if (this.controls.LEFT)
                    {
                        this.projectile.angleControl(9, 210);
                    }
                    else
                    {
                        if (this.controls.RIGHT)
                        {
                            this.projectile.angleControl(9, 240);
                        }
                        else
                        {
                            this.projectile.angleControl(9, 225);
                        };
                    };
                };
                this.self.playSound("bmfire");
            };
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

