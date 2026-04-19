// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Grab_106

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Grab_106 extends MovieClip 
    {

        internal var attackBox:MovieClip;
        internal var grabBox:MovieClip;
        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var touchBox:MovieClip;
        internal var self:BlackMageExt;
        internal var xframe:String;
        internal var curSpeed:*;
        internal var xDecay:*;
        internal var xDecayPivot:*;
        internal var isMovingRight:*;
        internal var rand:int;

        public function Grab_106()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 15, this.frame16, 16, this.frame17, 20, this.frame21, 21, this.frame22, 24, this.frame25, 36, this.frame37, 37, this.frame38, 38, this.frame39, 39, this.frame40, 40, this.frame41, 42, this.frame43, 49, this.frame50);
        }

        public function xSpeedDecay():void
        {
            if (((this.self.getXSpeed() == 0) || (!(this.isMovingRight == (this.self.getXSpeed() > 0)))))
            {
                this.self.setXSpeed(0);
                this.self.destroyTimer(this.xSpeedDecay);
                return;
            };
            this.curSpeed = (this.curSpeed - ((this.isMovingRight == this.self.isFacingRight()) ? this.xDecay : this.xDecayPivot));
            if (this.curSpeed > 0)
            {
                this.self.setXSpeed(((this.isMovingRight) ? this.curSpeed : -(this.curSpeed)));
            }
            else
            {
                this.self.setXSpeed(0);
                this.self.destroyTimer(this.xSpeedDecay);
            };
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:MovieClip;
            var _local_6:MovieClip;
            var _local_7:BlackMageExt;
            var _local_8:String;
            var _local_9:*;
            var _local_10:*;
            var _local_11:*;
            var _local_12:*;
            var _local_13:int;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            this.xframe = "grab";
            if (((this.self) && (SSF2API.isReady())))
            {
                this.self.setXSpeed((this.self.getXSpeed() * 0.6));
            };
        }

        internal function frame3():*
        {
            SSF2API.playSound("grab_swing3");
        }

        internal function frame4():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-7)});
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }

        internal function frame17():*
        {
            this.xframe = "grab";
            this.curSpeed = this.self.getCharacterStat("max_xSpeed");
            this.xDecay = 0.6;
            this.xDecayPivot = 0.9;
            this.isMovingRight = (this.self.getXSpeed() > 0);
            this.self.createTimer(1, -1, this.xSpeedDecay);
            this.self.addEventListener(SSF2Event.CHAR_GRAB, function (_arg_1:*=null):*
            {
                self.destroyTimer(xSpeedDecay);
            });
        }

        internal function frame21():*
        {
            SSF2API.playSound("grab_swing5");
        }

        internal function frame22():*
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-7),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame25():*
        {
            this.self.destroyTimer(this.xSpeedDecay);
        }

        internal function frame37():*
        {
            this.self.endAttack();
        }

        internal function frame38():*
        {
            this.self.addEffectToList(this.self.attachEffect("grabbed_gfx", {
                "x":this.self.flipX(23),
                "y":-15,
                "scaleX":-0.4,
                "scaleY":-0.4
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame39():*
        {
            stop();
            this.xframe = "grab";
            this.rand = 0;
            if (((this.self.isCPU()) && (this.self.getCPULevel() >= 1)))
            {
                this.rand = (10 * SSF2API.random());
                if (this.rand >= 6)
                {
                    this.self.stancePlayFrame("attack");
                };
            };
        }

        internal function frame40():*
        {
            this.self.stancePlayFrame("grabbed2");
        }

        internal function frame41():*
        {
            this.xframe = "attack";
            this.self.updateAttackBoxStats(1, {"effect_id":"effect_lightHit"});
        }

        internal function frame43():*
        {
            this.self.addEffectToList(this.self.attachEffect("trail_bmage_pummel", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-5)});
            this.self.clearEffectsOnStateChange();
            this.self.refreshAttackID();
        }

        internal function frame50():*
        {
            this.self.stancePlayFrame("grabbed2");
        }


    }
}//package blackmage_fla

