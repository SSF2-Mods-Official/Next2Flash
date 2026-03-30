package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class DoubleJump_25 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var xframe:*;
        public var done:*;
        public var fatjump:*;

        public function DoubleJump_25()
        {
            super();
            addFrameScript(0, this.frame1, 18, this.frame19);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getGlobalVariable("screwAttackOn") && (this.self.getMidairJumpCount() < 2))
                {
                    this.self.forceAttack("item_screw");
                }
                else if (this.self.getGlobalVariable("sonicShieldFiredash") && (this.self.getControls().LEFT || this.self.getControls().RIGHT))
                {
                    this.self.forceAttack("item_firedash");
                }
                else if (this.self.getGlobalVariable("sonicShieldBubbleBounce") && this.self.getControls().DOWN)
                {
                    this.self.forceAttack("item_bubblebounce");
                }
                else
                {
                    this.xframe = "midair";
                    this.done = false;
                    this.fatjump = false;
                    this.self.setGlobalVariable("kirbyPeachUsed", false);
                    if (this.self.getMidairJumpCount() == 1)
                    {
                        this.self.playSound("bandanadee_jump2");
                    }
                    else if (this.self.getMidairJumpCount() == 2)
                    {
                        this.self.playSound("bandanadee_jump3");
                    }
                    else if (this.self.getMidairJumpCount() == 3)
                    {
                        this.self.playSound("bandanadee_jump4");
                    };
                };
            };
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }


    }
}

