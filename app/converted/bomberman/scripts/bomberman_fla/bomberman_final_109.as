package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_final_109 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var self:BombermanExt;
        public var timer:Number;
        public var target:*;
        public var cpuUP:Boolean;
        public var finalSmashBar:FinalSmashBar;
        public var speedX:Number;
        public var speedY:Number;
        public var curSpeedX:Number;
        public var curSpeedY:Number;
        public var accel:Number;
        public var prevGrav:Number;
        public var controls:Object;
        public var moveTimer:Number;
        public var cam:*;
        public var yTeleport:*;
        public var xTeleport:*;
        public var firstTime:*;

        public function bomberman_final_109()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 27, this.frame28, 36, this.frame37, 64, this.frame65, 65, this.frame66, 70, this.frame71, 76, this.frame77, 82, this.frame83, 83, this.frame84, 84, this.frame85, 86, this.frame87, 88, this.frame89, 89, this.frame90, 105, this.frame106, 106, this.frame107);
        }

        public function setupBar():*
        {
            this.finalSmashBar = new FinalSmashBar(this.timer);
            this.finalSmashBar.addToDamageMeter(this.self.getHealthBox());
            this.self.setFinalSmashMeterCharge(0);
            this.self.addEventListener(SSF2Event.CHAR_KO_DEATH, this.clearBar, {"persistent":true});
        }

        public function clearBar(_arg_1:*=null):*
        {
            this.finalSmashBar.removeFromDamageMeter(this.self.getHealthBox());
            this.finalSmashBar = null;
            this.self.removeEventListener(SSF2Event.CHAR_KO_DEATH, this.clearBar);
        }

        public function resetGravity(_arg_1:*=null):*
        {
            this.self.updateCharacterStats({"gravity":this.prevGrav});
        }

        public function processControls(_arg_1:*=null):*
        {
            if (this.moveTimer > 0)
            {
                this.moveTimer--;
            };
            this.controls = this.self.getControls();
            if (this.controls.RIGHT && !(this.controls.LEFT))
            {
                this.speedX = 9;
            }
            else if (this.controls.LEFT && !(this.controls.RIGHT))
            {
                this.speedX = -9;
            }
            else
            {
                this.speedX = 0;
            };
            if (this.controls.UP && !(this.controls.DOWN))
            {
                this.speedY = -7;
            }
            else if (this.controls.DOWN && !(this.controls.UP))
            {
                this.speedY = 7;
            }
            else
            {
                this.speedY = 0;
            };
            this.smoothSpeed();
            this.self.setXSpeed(this.curSpeedX);
            this.self.setYSpeed(this.curSpeedY);
            this.timer--;
            this.finalSmashBar.updateBar(this.timer);
            if (this.timer < 0)
            {
                this.self.updateAttackStats({"air_ease":0});
                this.resetGravity();
                this.self.stancePlayFrame("finish");
            };
        }

        public function smoothSpeed():*
        {
            if (this.speedX > this.curSpeedX)
            {
                if ((this.curSpeedX < 0) && (this.speedX == 0) && ((this.curSpeedX + this.accel) > 0))
                {
                    this.curSpeedX = 0;
                }
                else
                {
                    this.curSpeedX += this.accel;
                    if ((this.speedX > 0) && (this.curSpeedX < 0))
                    {
                        this.curSpeedX += this.accel;
                    };
                };
            };
            if (this.speedX < this.curSpeedX)
            {
                if ((this.curSpeedX > 0) && (this.speedX == 0) && ((this.curSpeedX - this.accel) < 0))
                {
                    this.curSpeedX = 0;
                }
                else
                {
                    this.curSpeedX -= this.accel;
                    if ((this.speedX < 0) && (this.curSpeedX > 0))
                    {
                        this.curSpeedX -= this.accel;
                    };
                };
            };
            if (this.speedY > this.curSpeedY)
            {
                if ((this.curSpeedY < 0) && (this.speedY == 0) && ((this.curSpeedY + this.accel) > 0))
                {
                    this.curSpeedY = 0;
                }
                else
                {
                    this.curSpeedY += this.accel;
                    if ((this.speedY > 0) && (this.curSpeedY < 0))
                    {
                        this.curSpeedX += this.accel;
                    };
                };
            };
            if (this.speedY < this.curSpeedY)
            {
                if ((this.curSpeedY > 0) && (this.speedY == 0) && ((this.curSpeedY - this.accel) < 0))
                {
                    this.curSpeedY = 0;
                }
                else
                {
                    this.curSpeedY -= this.accel;
                    if ((this.speedY < 0) && (this.curSpeedY > 0))
                    {
                        this.curSpeedY -= this.accel;
                    };
                };
            };
            if (((this.curSpeedX > this.speedX) && (this.speedX > 0)) || ((this.curSpeedX < this.speedX) && (this.speedX < 0)))
            {
                this.curSpeedX = this.speedX;
            }
            else if (((this.curSpeedY > this.speedY) && (this.speedY > 0)) || ((this.curSpeedY < this.speedY) && (this.speedY < 0)))
            {
                this.curSpeedY = this.speedY;
            };
        }

        public function timeDown(_arg_1:*=null):*
        {
            this.timer--;
            if (this.finalSmashBar != null)
            {
                this.finalSmashBar.updateBar(this.timer);
            };
        }

        public function dropNormal():*
        {
            this.self.fireProjectile("FSbomb");
            this.self.getCurrentProjectile().updateProjectileStats({"maxgravity":13});
        }

        public function dropBig():*
        {
            this.self.fireProjectile("medFSbomb");
            this.self.getCurrentProjectile().updateProjectileStats({"maxgravity":16});
        }

        public function dropPower():*
        {
            this.self.fireProjectile("bigFSbomb");
        }

        public function dropCross():*
        {
            this.self.fireProjectile("crossFSbomb");
            this.self.getCurrentProjectile().updateProjectileStats({"maxgravity":10});
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            this.timer = 360;
            this.target = null;
            this.cpuUP = false;
            this.speedX = 0;
            this.speedY = 0;
            this.curSpeedX = 0;
            this.curSpeedY = 0;
            this.accel = 1;
            this.moveTimer = 0;
            if (SSF2API.isReady())
            {
                this.self.unnattachFromGround();
                SSF2API.getCamera().killDarkener(true);
            };
        }

        internal function frame3():*
        {
            this.self.playAttackSound(1);
            this.self.updateAttackStats({"air_ease":0});
        }

        internal function frame28():*
        {
            this.self.playAttackSound(2);
            this.self.attachEffect("effect_explosion", {
                "x":this.self.flipX(10),
                "scaleX":1.5,
                "scaleY":1.5
            });
            SSF2API.getCamera().shake(12);
        }

        internal function frame37():*
        {
            this.cam = SSF2API.getStage().getCameraBounds();
            this.yTeleport = (this.cam.y + 150);
            this.xTeleport = (this.cam.x + (this.cam.width / 2));
            this.self.updateAttackStats({"air_ease":0});
            this.self.setX(this.xTeleport);
            this.self.setY(this.yTeleport);
            this.setupBar();
        }

        internal function frame65():*
        {
            this.self.createTimer(1, -1, this.processControls);
            this.self.stancePlayFrame("loop");
            this.self.updateAttackStats({
                "allowControl":true,
                "air_ease":-1
            });
            this.prevGrav = this.self.getCharacterStat("gravity");
            this.self.updateCharacterStats({"gravity":0});
            this.self.addEventListener(SSF2Event.STATE_CHANGE, this.resetGravity);
            this.self.createTimer(1, -1, this.timeDown);
            this.firstTime = true;
        }

        internal function frame66():*
        {
            if (this.firstTime)
            {
                this.dropNormal();
            };
        }

        internal function frame71():*
        {
            this.dropBig();
            this.self.playAttackSound(3);
        }

        internal function frame77():*
        {
            this.dropPower();
            this.self.playAttackSound(3);
        }

        internal function frame83():*
        {
            this.dropNormal();
            this.self.playAttackSound(3);
            this.firstTime = false;
        }

        internal function frame84():*
        {
            if (this.timer <= 0)
            {
                this.self.stancePlayFrame("finish");
            }
            else
            {
                this.self.stancePlayFrame("loop");
            };
        }

        internal function frame85():*
        {
            this.self.destroyTimer(this.processControls);
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.resetMovement();
        }

        internal function frame87():*
        {
            this.dropCross();
            this.self.playAttackSound(3);
        }

        internal function frame89():*
        {
            this.self.updateAttackStats({"allowControl":false});
        }

        internal function frame90():*
        {
            this.clearBar();
            this.self.playAttackSound(4);
        }

        internal function frame106():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.resetMovement();
                this.self.updateAttackStats({"allowControl":true});
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame107():*
        {
            this.self.endAttack();
        }


    }
}

