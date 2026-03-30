package bomberman_fla
{
    import flash.display.MovieClip;
    import flash.events.Event;

    public dynamic class bomberman_fspec_air_41 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var reverseBox:MovieClip;
        public var self:BombermanExt;
        public var controls:*;
        public var dir:Boolean;
        public var bombArray:*;
        public var bomb:*;
        public var teamArray:*;
        public var combinedArray:*;
        public var teammates:*;
        public var teammate:*;
        public var chargeSpeed:Number;
        public var t:int;
        public var i:int;
        public var xPosN:*;
        public var yPosN:*;

        public function bomberman_fspec_air_41()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 5, this.frame6, 6, this.frame7, 8, this.frame9, 13, this.frame14, 14, this.frame15, 15, this.frame16, 16, this.frame17, 17, this.frame18, 18, this.frame19, 19, this.frame20, 20, this.frame21, 21, this.frame22, 22, this.frame23, 23, this.frame24, 24, this.frame25);
        }

        public function jumpToContinue(_arg_1:Event=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            this.self.updateAttackStats({"allowControl":false});
            gotoAndStop("continue");
        }

        public function flipX(_arg_1:Number):*
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        public function reflected(_arg_1:*=null):*
        {
            this.self.playSound("reflect_sfx");
            SSF2API.attachEffect("reflect_effect", {
                "x":_arg_1.data.opponent.getX(),
                "y":_arg_1.data.opponent.getY()
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (SSF2API.isReady())
            {
                this.controls = this.self.getControls();
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
                this.self.addEventListener(SSF2Event.REVERSE_HIT, this.reflected);
            };
            this.bombArray = null;
            this.teamArray = null;
            this.combinedArray = null;
            this.teammates = null;
            this.teammate = null;
        }

        internal function frame4():*
        {
            this.self.addEffectToList(this.self.attachEffect("trail_bbm_sspeca", {
                "scaleX":1.35,
                "scaleY":1.35,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame5():*
        {
            this.chargeSpeed = 28;
            this.bombArray = this.self.bombArray;
            this.teammates = this.self.getTeammates();
            if (this.teammates != null)
            {
                this.t = 0;
                while (this.t < this.teammates.length)
                {
                    if (this.teammates[this.t].isDisposed())
                    {
                        continue;
                    };
                    if (this.teammates[this.t].getLinkageID() == "bomberman")
                    {
                        SSF2API.print((("teammate number" + (this.t + 1)) + " is bomberman!"));
                        if (this.teamArray == null)
                        {
                            this.teamArray = this.teammates[this.t].bombArray;
                        }
                        else if ((this.teammates[this.t].bombArray != null) && (this.teammates != null) && (this.teammates[this.t].bombArray != null))
                        {
                            this.teamArray = this.teamArray.concat(this.teammates[this.t].bombArray);
                        };
                    };
                    this.t++;
                };
            };
            if (this.teamArray != null)
            {
                if (this.bombArray != null)
                {
                    this.combinedArray = this.bombArray.concat(this.teamArray);
                }
                else
                {
                    this.combinedArray = this.teamArray;
                };
                SSF2API.print("Added the teammate(s) bombs to yours.");
            }
            else
            {
                this.combinedArray = this.bombArray;
                SSF2API.print("The teammate(s) had no bombs.");
            };
            if (this.combinedArray != null)
            {
                this.i = 0;
                while (this.i < this.combinedArray.length)
                {
                    this.bomb = this.combinedArray[this.i];
                    if (this.bomb.isDisposed())
                    {
                        continue;
                    };
                    this.xPosN = (this.bomb.getX() - this.self.getX());
                    this.yPosN = Math.abs((this.bomb.getY() - this.self.getY()));
                    this.dir = this.self.isFacingRight();
                    if (this.dir)
                    {
                        if ((this.xPosN > -10) && (this.xPosN < 55) && (this.yPosN < 50))
                        {
                            if (!(this.bomb.inState(PState.DEAD)) && this.bomb)
                            {
                                SSF2API.print("bomb found! kicking...");
                                this.self.forceHitStun(2, 0);
                                this.bomb.forceHitStun(2, 0);
                                this.self.playSound("brawl_punch_s");
                                this.bomb.setXSpeed(((this.chargeSpeed * Math.cos(SSF2Utils.toRadians(45))) / 2));
                                this.bomb.setYSpeed((((-1 * this.chargeSpeed) * Math.sin(SSF2Utils.toRadians(45))) / 2));
                                this.bomb.getStanceMC().gotoAndStop("kickedRight");
                            }
                            else
                            {
                                this.i--;
                                this.combinedArray.splice(this.i, 1);
                            };
                        };
                    }
                    else if ((this.xPosN > -55) && (this.xPosN < 10) && (this.yPosN < 50))
                    {
                        if (!(this.bomb.inState(PState.DEAD)) && this.bomb)
                        {
                            SSF2API.print("bomb found! kicking...");
                            this.self.forceHitStun(2, 0);
                            this.bomb.forceHitStun(2, 0);
                            this.self.playSound("brawl_punch_s");
                            this.bomb.setXSpeed((((-1 * this.chargeSpeed) * Math.cos(SSF2Utils.toRadians(45))) / 2));
                            this.bomb.setYSpeed((((-1 * this.chargeSpeed) * Math.sin(SSF2Utils.toRadians(45))) / 2));
                            this.bomb.getStanceMC().gotoAndStop("kickedLeft");
                        }
                        else
                        {
                            this.i--;
                            this.combinedArray.splice(this.i, 1);
                        };
                    };
                    this.i++;
                };
            };
        }

        internal function frame6():*
        {
            this.self.attachEffect("global_spark", {
                "x":this.flipX(50),
                "y":-25
            });
            this.self.playAttackSound(1);
        }

        internal function frame7():*
        {
            this.self.setYSpeed(-10);
        }

        internal function frame9():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
        }

        internal function frame14():*
        {
            this.controls = this.self.getControls();
            if (this.controls.DOWN && this.controls.BUTTON1)
            {
                this.self.forceAttack("b_down");
            };
        }

        internal function frame15():*
        {
            this.controls = this.self.getControls();
            if (this.controls.DOWN && this.controls.BUTTON1)
            {
                this.self.forceAttack("b_down");
            };
        }

        internal function frame16():*
        {
            this.controls = this.self.getControls();
            if (this.controls.DOWN && this.controls.BUTTON1)
            {
                this.self.forceAttack("b_down");
            };
        }

        internal function frame17():*
        {
            this.controls = this.self.getControls();
            if (this.controls.DOWN && this.controls.BUTTON1)
            {
                this.self.forceAttack("b_down");
            };
        }

        internal function frame18():*
        {
            this.self.endAttack();
            this.controls = this.self.getControls();
            if (this.controls.DOWN && this.controls.BUTTON1)
            {
                this.self.forceAttack("b_down");
            };
        }

        internal function frame19():*
        {
            this.self.removeAllEffects();
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            };
            this.controls = this.self.getControls();
            if (this.controls.DOWN && this.controls.BUTTON1)
            {
                this.self.forceAttack("b_down");
            };
        }

        internal function frame20():*
        {
            this.controls = this.self.getControls();
            if (this.controls.DOWN && this.controls.BUTTON1)
            {
                this.self.forceAttack("b_down");
            };
        }

        internal function frame21():*
        {
            this.controls = this.self.getControls();
            if (this.controls.DOWN && this.controls.BUTTON1)
            {
                this.self.forceAttack("b_down");
            };
        }

        internal function frame22():*
        {
            this.controls = this.self.getControls();
            if (this.controls.DOWN && this.controls.BUTTON1)
            {
                this.self.forceAttack("b_down");
            };
        }

        internal function frame23():*
        {
            this.controls = this.self.getControls();
            if (this.controls.DOWN && this.controls.BUTTON1)
            {
                this.self.forceAttack("b_down");
            };
        }

        internal function frame24():*
        {
            this.controls = this.self.getControls();
            if (this.controls.DOWN && this.controls.BUTTON1)
            {
                this.self.forceAttack("b_down");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

