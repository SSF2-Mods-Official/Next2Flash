// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.DSpecial_67

package blackmage_fla
{
    import flash.display.MovieClip;
    import flash.geom.*;
    import flash.display.*;
    import flash.events.*;
    import flash.media.*;
    import flash.filters.*;
    import flash.utils.*;
    import adobe.utils.*;
    import flash.accessibility.*;
    import flash.desktop.*;
    import flash.errors.*;
    import flash.external.*;
    import flash.globalization.*;
    import flash.net.*;
    import flash.net.drm.*;
    import flash.printing.*;
    import flash.profiler.*;
    import flash.sampler.*;
    import flash.sensors.*;
    import flash.system.*;
    import flash.text.*;
    import flash.text.ime.*;
    import flash.text.engine.*;
    import flash.ui.*;
    import flash.xml.*;

    public dynamic class DSpecial_67 extends MovieClip 
    {

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

        public function DSpecial_67()
        {
            addFrameScript(0, this.frame1, 4, this.frame5, 10, this.frame11, 11, this.frame12, 14, this.frame15, 15, this.frame16, 25, this.frame26, 27, this.frame28, 33, this.frame34, 53, this.frame54);
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
                this.self.stancePlayFrame("broken");
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

        public function projExists():Boolean
        {
            return (((!(this.projectile == null)) && (!(this.projectile.isDisposed()))) && (!(this.projectile.inState(PState.DEAD))));
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            this.MENAH = 5;
            if (((this.self) && (SSF2API.isReady())))
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

        internal function frame5():*
        {
            this.projectile = this.self.fireProjectile("meteor");
            this.self.setGlobalVariable("BMageDSpecProj", this.projectile);
            this.projectile.addToCamera();
            this.self.attachEffect("global_spark", {"x":this.self.flipX(18)});
            SSF2API.getCamera().shake(3);
            this.curFrame = 0;
        }

        internal function frame11():*
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON1)
            {
                this.self.createTimer(1, -1, this.checkProjectile);
                this.self.stancePlayFrame("attack");
            };
        }

        internal function frame12():*
        {
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

        internal function frame15():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame16():*
        {
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

        internal function frame26():*
        {
            this.self.attachEffect("global_sparkle", {
                "x":this.self.flipX(15),
                "y":-30
            });
        }

        internal function frame28():*
        {
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

        internal function frame34():*
        {
            this.self.endAttack();
        }

        internal function frame54():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

