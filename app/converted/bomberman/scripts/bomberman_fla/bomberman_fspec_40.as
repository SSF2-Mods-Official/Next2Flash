package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_fspec_40 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var reverseBox:MovieClip;
        public var self:BombermanExt;
        public var character:*;
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

        public function bomberman_fspec_40()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 3, this.frame4, 5, this.frame6, 6, this.frame7, 7, this.frame8, 8, this.frame9, 10, this.frame11);
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
            if (this.self && SSF2API.isReady())
            {
                this.character = this.self;
                this.controls = this.character.getControls();
                this.self.addEventListener(SSF2Event.REVERSE_HIT, this.reflected);
            };
            this.bombArray = null;
            this.teamArray = null;
            this.combinedArray = null;
            this.teammates = null;
            this.teammate = null;
        }

        internal function frame2():*
        {
            this.self.attachEffect("global_smash_spark", {
                "x":this.self.flipX(-12.5),
                "y":-11.5
            });
        }

        internal function frame3():*
        {
            this.chargeSpeed = 25;
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
                                this.bomb.setXSpeed(this.chargeSpeed);
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
                            this.bomb.setXSpeed((this.chargeSpeed * -1));
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
            this.self.attachEffect("global_dust_light");
            this.self.addEffectToList(this.self.attachEffect("trail_bbm_sspecg", {
                "scaleX":1.35,
                "scaleY":1.35,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame4():*
        {
            this.self.attachEffect("global_spark", {
                "x":this.flipX(50),
                "y":-25
            });
            this.self.playAttackSound(1);
        }

        internal function frame6():*
        {
            this.controls = this.character.getControls();
            if (this.controls.DOWN && this.controls.BUTTON1)
            {
                this.character.forceAttack("b_down");
            };
        }

        internal function frame7():*
        {
            this.controls = this.character.getControls();
            if (this.controls.DOWN && this.controls.BUTTON1)
            {
                this.character.forceAttack("b_down");
            };
        }

        internal function frame8():*
        {
            this.controls = this.character.getControls();
            if (this.controls.DOWN && this.controls.BUTTON1)
            {
                this.character.forceAttack("b_down");
            };
        }

        internal function frame9():*
        {
            this.controls = this.character.getControls();
            if (this.controls.DOWN && this.controls.BUTTON1)
            {
                this.character.forceAttack("b_down");
            };
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            };
        }

        internal function frame11():*
        {
            this.self.endAttack();
        }


    }
}

