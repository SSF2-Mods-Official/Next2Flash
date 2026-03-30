package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_dspec_42 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;
        public var character:*;
        public var dir:Boolean;
        public var bomb:*;
        public var teamArray:Array;
        public var combinedArray:Array;
        public var teammates:*;
        public var teammate:*;
        public var playedSound:*;
        public var controls:Object;
        public var detonateAll:Boolean;
        public var tbd:*;
        public var t:int;
        public var i:int;

        public function bomberman_dspec_42()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 4, this.frame5, 8, this.frame9, 11, this.frame12);
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (this.self && SSF2API.isReady())
            {
                this.character = this.self;
            };
            this.teamArray = null;
            this.combinedArray = null;
            this.teammates = null;
            this.teammate = null;
            this.playedSound = false;
            this.detonateAll = true;
            this.tbd = false;
        }

        internal function frame2():*
        {
            this.self.attachEffect("global_sparkle", {
                "x":this.flipX(-10),
                "y":-50
            });
        }

        internal function frame5():*
        {
            if (this.tbd == false)
            {
                this.self.playAttackSound(1);
                if (this.self.bombArray != null)
                {
                    while (this.self.bombArray.length)
                    {
                        this.bomb = this.self.bombArray.shift();
                        if (!(this.bomb.isDisposed()) && !(this.bomb.inState(PState.DEAD)))
                        {
                            if (!this.playedSound)
                            {
                                this.self.playAttackSound(2);
                                this.playedSound = true;
                            };
                            this.bomb.getStanceMC().gotoAndStop("continue");
                        };
                    };
                };
            }
            else if (this.tbd == true)
            {
                this.self.playAttackSound(1);
                this.teammates = this.self.getTeammates();
                if (this.teammates != null)
                {
                    this.t = 0;
                    while (this.t < this.teammates.length)
                    {
                        if (this.teammates[this.t].getLinkageID() == "bomberman")
                        {
                            SSF2API.print((("teammate number" + (this.t + 1)) + " is bomberman!"));
                            if (this.teamArray == null)
                            {
                                this.teamArray = this.teammates[this.t].getGlobalVariable("bombArray");
                            }
                            else if (this.teammates[this.t].getGlobalVariable("bombArray") != null)
                            {
                                this.teamArray = this.teamArray.concat(this.teammates[this.t].getGlobalVariable("bombArray"));
                            };
                        };
                        this.t++;
                    };
                };
                if (this.teamArray != null)
                {
                    if (this.self.bombArray != null)
                    {
                        this.combinedArray = this.teamArray.concat(this.self.bombArray);
                    }
                    else
                    {
                        this.combinedArray = this.teamArray;
                    };
                    SSF2API.print("Added the teammate(s) bombs to yours.");
                }
                else
                {
                    this.combinedArray = this.self.bombArray;
                    SSF2API.print("The teammate(s) had no bombs.");
                };
                if (this.combinedArray != null)
                {
                    this.i = 0;
                    while (this.i < this.combinedArray.length)
                    {
                        this.bomb = this.combinedArray[this.i];
                        if (!(this.bomb.isDisposed()) && !(this.bomb.inState(PState.DEAD)))
                        {
                            if (!this.playedSound)
                            {
                                this.self.playAttackSound(2);
                                this.playedSound = true;
                            };
                            this.bomb.getStanceMC().gotoAndStop("continue");
                        }
                        else
                        {
                            this.i--;
                            this.combinedArray.splice(this.i, 1);
                        };
                        this.i++;
                    };
                };
            };
        }

        internal function frame9():*
        {
            this.self.attachEffect("dust", {"y":-20});
        }

        internal function frame12():*
        {
            this.self.endAttack();
        }


    }
}

