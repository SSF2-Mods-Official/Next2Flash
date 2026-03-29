package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class DSpecial_52 extends MovieClip
    {

        public var absorbBox:MovieClip;
        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;
        public var chargeLevel:*;
        public var CHARGE_LEVEL_MAX:*;
        public var chargeDamage:*;
        public var frameCount:*;
        public var controls:*;
        public var canTurn:Boolean;
        public var turnFrame:Number;
        public var timerRunning:Boolean;
        public var sfxAttack:*;

        public function DSpecial_52()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 8, this.frame9, 9, this.frame10, 14, this.frame15, 18, this.frame19, 19, this.frame20, 24, this.frame25, 28, this.frame29, 29, this.frame30, 34, this.frame35, 38, this.frame39, 39, this.frame40, 53, this.frame54, 55, this.frame56, 61, this.frame62);
        }

        public function setData():*
        {
            this.self.setGlobalVariable("chargeLevel", this.chargeLevel);
            this.self.setGlobalVariable("damage", this.chargeDamage);
        }

        public function getData():*
        {
            this.chargeLevel = this.self.getGlobalVariable("chargeLevel");
            this.chargeDamage = this.self.getGlobalVariable("damage");
            this.chargeLevel = ((this.chargeLevel == null) ? 0 : this.chargeLevel);
            this.chargeDamage = ((this.chargeDamage == null) ? 0 : this.chargeDamage);
        }

        public function absorb(_arg_1:*):void
        {
            this.self.attachEffect("global_sparkle", {
                "x":20,
                "y":-5
            });
            this.chargeDamage += (_arg_1.data.attackBoxData.damage * 1.5);
            this.chargeLevel++;
            this.setData();
            SSF2API.print(((("chargeLevel: " + this.chargeLevel) + "\ndamage: ") + this.chargeDamage));
            this.goTo(true);
            _arg_1.data.projectile.destroy();
        }

        public function startTimer(_arg_1:Boolean=true):*
        {
            if (_arg_1)
            {
                if (!this.timerRunning)
                {
                    this.self.createTimer(1, -1, this.buttonCheck);
                    this.timerRunning = true;
                };
            }
            else
            {
                this.self.destroyTimer(this.buttonCheck);
                this.timerRunning = false;
            };
        }

        public function buttonCheck():*
        {
            this.controls = this.self.getControls();
            this.turnFrame++;
            if (this.canTurn && (this.turnFrame > 3))
            {
                if ((this.controls.LEFT && !(this.controls.RIGHT) && this.self.isFacingRight()) || (this.controls.RIGHT && !(this.controls.LEFT) && !(this.self.isFacingRight())))
                {
                    this.self.flip();
                    this.turnFrame = 0;
                };
            };
            SSF2API.print(this.turnFrame.toString());
            if (!(this.controls.BUTTON1) && (this.frameCount >= 12))
            {
                this.self.stancePlayFrame("end");
            };
        }

        public function goTo(_arg_1:Boolean=false):*
        {
            this.self.attachEffect("global_spark");
            if (this.chargeLevel > 0)
            {
                if (_arg_1)
                {
                    this.self.stancePlayFrame(("to" + this.chargeLevel));
                }
                else
                {
                    this.self.stancePlayFrame(("level" + this.chargeLevel));
                };
            };
        }

        public function countingFrames():*
        {
            this.frameCount++;
        }

        public function stopSfx(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.CHAR_HURT, this.stopSfx);
            this.self.removeEventListener(SSF2Event.CHAR_KO_DEATH, this.stopSfx);
            this.self.removeEventListener(SSF2Event.CHAR_GRABBED, this.stopSfx);
            if (this.sfxAttack)
            {
                SSF2API.stopSound(this.sfxAttack);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            this.CHARGE_LEVEL_MAX = 3;
            this.frameCount = 0;
            this.canTurn = false;
            this.turnFrame = 0;
            this.timerRunning = false;
            if (this.self && SSF2API.isReady())
            {
                if (this.self.getYSpeed() < 0)
                {
                    this.self.setYSpeed(0);
                };
                this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
                this.getData();
                if (this.chargeLevel < this.CHARGE_LEVEL_MAX)
                {
                    this.self.attachEffect("global_sparkle", {
                        "x":20,
                        "y":-5
                    });
                    SSF2API.print(((("chargeLevel: " + this.chargeLevel) + "\ndamage: ") + this.chargeDamage));
                    this.self.addEventListener(SSF2Event.CHAR_ABSORB, this.absorb);
                }
                else
                {
                    this.self.stancePlayFrame("fire");
                };
            };
        }

        internal function frame3():*
        {
            this.self.playSound("beep_high");
            this.self.createTimer(1, -1, this.countingFrames);
            this.startTimer();
            this.canTurn = true;
            this.goTo();
        }

        internal function frame9():*
        {
            this.self.stancePlayFrame("level0");
        }

        internal function frame10():*
        {
            this.startTimer(false);
            this.canTurn = false;
            this.self.playSound("beep_high");
        }

        internal function frame15():*
        {
            this.startTimer();
            this.canTurn = true;
        }

        internal function frame19():*
        {
            this.self.stancePlayFrame("level1");
        }

        internal function frame20():*
        {
            this.startTimer(false);
            this.canTurn = false;
            this.self.playSound("beep_high");
        }

        internal function frame25():*
        {
            this.startTimer();
            this.canTurn = true;
        }

        internal function frame29():*
        {
            this.self.stancePlayFrame("level2");
        }

        internal function frame30():*
        {
            this.startTimer(false);
            this.canTurn = false;
            this.self.playSound("beep_high");
        }

        internal function frame35():*
        {
            this.self.endAttack();
        }

        internal function frame39():*
        {
            this.self.stancePlayFrame("end");
        }

        internal function frame40():*
        {
            this.startTimer(false);
            this.canTurn = false;
            if (this.chargeDamage < 15)
            {
                this.chargeDamage = 15;
            }
            else if (this.chargeDamage > 60)
            {
                this.chargeDamage = 60;
            };
            this.self.updateAttackBoxStats(1, {"damage":this.chargeDamage});
            this.chargeLevel = 0;
            this.chargeDamage = 0;
            this.setData();
            this.sfxAttack = this.self.playSound("gw_taunt");
            this.self.addEventListener(SSF2Event.CHAR_HURT, this.stopSfx, {"persistent":true});
            this.self.addEventListener(SSF2Event.CHAR_KO_DEATH, this.stopSfx, {"persistent":true});
            this.self.addEventListener(SSF2Event.CHAR_GRABBED, this.stopSfx, {"persistent":true});
        }

        internal function frame54():*
        {
            this.self.removeEventListener(SSF2Event.CHAR_HURT, this.stopSfx);
            this.self.removeEventListener(SSF2Event.CHAR_KO_DEATH, this.stopSfx);
            this.self.removeEventListener(SSF2Event.CHAR_GRABBED, this.stopSfx);
            SSF2API.stopSound(this.sfxAttack);
        }

        internal function frame56():*
        {
            this.startTimer(false);
        }

        internal function frame62():*
        {
            this.self.endAttack();
        }


    }
}

