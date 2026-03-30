package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Pac_ManKirby_279 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var itemMC:MovieClip;
        public var self:KirbyExt;
        public var controls:Object;
        public var released:Boolean;
        public var canThrow:Boolean;
        public var finalFruit:Number;
        public var fruitMC:MovieClip;
        public var regrab:Boolean;
        public var tooEarly:Boolean;
        public var fruitName:String;
        public var item:*;

        public function Pac_ManKirby_279()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 4, this.frame5, 5, this.frame6, 12, this.frame13, 16, this.frame17, 20, this.frame21, 21, this.frame22, 24, this.frame25, 25, this.frame26, 26, this.frame27, 28, this.frame29, 33, this.frame34, 35, this.frame36);
        }

        public function checkThrow():void
        {
            this.controls = this.self.getControls();
            if (this.released && this.controls.BUTTON1 && this.canThrow)
            {
                this.self.destroyTimer(this.checkThrow);
                this.self.stancePlayFrame("throw");
            };
            this.released = (!(this.controls.BUTTON1));
            if (this.controls.SHIELD && this.canThrow)
            {
                this.self.removeEventListener(SSF2Event.CHAR_HURT, this.resetCharge);
                this.self.removeEventListener(SSF2Event.CHAR_GRABBED, this.resetCharge);
                this.self.endAttack();
            }
            else if (this.controls.LEFT && this.canThrow && this.self.isOnGround())
            {
                this.self.removeEventListener(SSF2Event.CHAR_HURT, this.resetCharge);
                this.self.removeEventListener(SSF2Event.CHAR_GRABBED, this.resetCharge);
                this.self.faceLeft();
                this.self.toDodgeRoll();
            }
            else if (this.controls.RIGHT && this.canThrow && this.self.isOnGround())
            {
                this.self.removeEventListener(SSF2Event.CHAR_HURT, this.resetCharge);
                this.self.removeEventListener(SSF2Event.CHAR_GRABBED, this.resetCharge);
                this.self.faceRight();
                this.self.toDodgeRoll();
            };
        }

        public function resetCharge(_arg_1:*):*
        {
            this.self.removeEventListener(SSF2Event.CHAR_HURT, this.resetCharge);
            this.self.removeEventListener(SSF2Event.CHAR_KO_DEATH, this.resetCharge);
            this.self.removeEventListener(SSF2Event.CHAR_GRABBED, this.resetCharge);
            this.self.fruit = 0;
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.released = false;
            this.canThrow = false;
            this.finalFruit = 0;
            this.fruitMC = null;
            this.regrab = false;
            this.tooEarly = false;
        }

        internal function frame2():*
        {
            this.self.createTimer(1, -1, this.checkThrow);
            this.self.addEventListener(SSF2Event.CHAR_HURT, this.resetCharge, {"persistent":true});
            this.self.addEventListener(SSF2Event.CHAR_KO_DEATH, this.resetCharge, {"persistent":true});
            this.self.addEventListener(SSF2Event.CHAR_GRABBED, this.resetCharge, {"persistent":true});
        }

        internal function frame5():*
        {
            this.self.attachEffect("global_sparkle", {
                "y":-30,
                "x":this.self.flipX(15)
            });
        }

        internal function frame6():*
        {
            this.self.removeLocked();
            if (!(this.canThrow) && (this.self.fruit == 8))
            {
                this.self.stancePlayFrame("throw");
            };
            if (this.self.fruit < 1)
            {
                this.self.fruit++;
            };
            this.canThrow = true;
            if ((this.self.fruit == 8) && this.canThrow)
            {
                this.self.attachEffect("global_sparkle", {
                    "y":-60,
                    "x":this.self.flipX(30)
                });
            };
            this.self.attachEffect("global_dust_light");
            this.fruitMC = this.self.lockEffect("pacman_nspec_effect", 0, 0);
            this.fruitMC.chargingFruit.gotoAndStop(((this.self.fruit * 2) - 1));
            if (!this.self.isFacingRight())
            {
                this.fruitMC.gotoAndStop("loopLeft");
            }
            else
            {
                this.fruitMC.gotoAndStop("loopRight");
            };
            if (this.self.fruit == 1)
            {
                this.self.playSound("pacman_nspec01");
            };
            if (this.self.fruit == 2)
            {
                this.self.playSound("pacman_nspec02");
            };
            if (this.self.fruit == 3)
            {
                this.self.playSound("pacman_nspec03");
            };
            if (this.self.fruit == 4)
            {
                this.self.playSound("pacman_nspec04");
            };
            if (this.self.fruit == 5)
            {
                this.self.playSound("pacman_nspec05");
            };
            if (this.self.fruit == 6)
            {
                this.self.playSound("pacman_nspec06");
            };
            if (this.self.fruit == 7)
            {
                this.self.playSound("pacman_nspec07");
            };
            if (this.self.fruit == 8)
            {
                this.self.playSound("pacman_nspec08");
            };
        }

        internal function frame13():*
        {
            if (this.self.fruit < 3)
            {
                this.self.fruit++;
                this.self.stancePlayFrame("loop");
            };
        }

        internal function frame17():*
        {
            if (this.self.fruit < 8)
            {
                this.self.fruit++;
                this.self.stancePlayFrame("loop");
            };
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }

        internal function frame22():*
        {
            this.self.removeEventListener(SSF2Event.CHAR_HURT, this.resetCharge);
            this.self.removeEventListener(SSF2Event.CHAR_KO_DEATH, this.resetCharge);
            this.self.removeEventListener(SSF2Event.CHAR_GRABBED, this.resetCharge);
            this.finalFruit = this.self.fruit;
            this.self.removeLocked();
            this.fruitMC = this.self.lockEffect("pacman_nspec_effect", 0, 0);
            this.fruitMC.chargingFruit.gotoAndStop(((this.self.fruit * 2) - 1));
            if (!this.self.isFacingRight())
            {
                this.fruitMC.gotoAndStop("throwLeft");
            }
            else
            {
                this.fruitMC.gotoAndStop("throwRight");
            };
            this.self.fruit = 0;
            this.canThrow = false;
            this.self.attachEffect("global_sparkle", {
                "x":this.self.flipX(22),
                "y":-20
            });
        }

        internal function frame25():*
        {
            this.controls = this.self.getControls();
            if (this.controls.SHIELD)
            {
                this.tooEarly = true;
            };
        }

        internal function frame26():*
        {
            this.self.attachEffect("global_dust_heavy");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            };
            this.controls = this.self.getControls();
            if (this.controls.SHIELD && !(this.tooEarly))
            {
                this.regrab = true;
            };
        }

        internal function frame27():*
        {
            switch (this.finalFruit)
            {
            case 1:
            this.fruitName = "pacman_cherry";
            break;
            case 2:
            this.fruitName = "pacman_strawberry";
            break;
            case 3:
            this.fruitName = "pacman_orange";
            break;
            case 4:
            this.fruitName = "pacman_apple";
            break;
            case 5:
            this.fruitName = "pacman_melon";
            break;
            case 6:
            this.fruitName = "pacman_galaxian";
            break;
            case 7:
            this.fruitName = "pacman_bell";
            break;
            case 8:
            this.fruitName = "pacman_key";
            break;
            case 8:
            default:
            this.fruitName = "pacman_cherry";
            break;
            }
            this.controls = this.self.getControls();
            if (this.controls.SHIELD && !(this.tooEarly) && !(this.regrab))
            {
                this.regrab = true;
            };
            if (this.regrab && !(this.self.getItem()))
            {
                this.item = this.self.generateItem(this.fruitName, true, true, true);
                if (this.self.isFacingRight())
                {
                    this.item.faceRight();
                }
                else
                {
                    this.item.faceLeft();
                };
            }
            else
            {
                this.regrab = false;
                this.item = this.self.generateItem(this.fruitName, false, true, true);
                this.item.setOwner(this.self);
                if (this.self.isFacingRight())
                {
                    this.item.setX((this.self.getX() + 24));
                    if (this.item.shouldFlip)
                    {
                        this.item.faceRight();
                    };
                }
                else
                {
                    this.item.setX((this.self.getX() - 24));
                    this.item.updateAttackBoxStats(1, {"direction":(-(this.item.getAttackBoxStat(1, "direction")) - 180)});
                    if (this.item.shouldFlip)
                    {
                        this.item.faceLeft();
                    };
                };
                this.item.setY((this.self.getY() - 6));
                this.item.toToss();
                this.self.playSound("item_throw");
            };
        }

        internal function frame29():*
        {
            if (this.regrab)
            {
                this.self.endAttack();
            };
        }

        internal function frame34():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            };
        }

        internal function frame36():*
        {
            this.self.endAttack();
        }


    }
}

