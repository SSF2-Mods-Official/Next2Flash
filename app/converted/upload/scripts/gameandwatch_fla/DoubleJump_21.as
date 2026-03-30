package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class DoubleJump_21 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;
        public var done:Boolean;
        public var xframe:*;

        public function DoubleJump_21()
        {
            super();
            addFrameScript(0, this.frame1, 21, this.frame22, 42, this.frame43);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (SSF2API.isReady() && this.self)
            {
                this.done = false;
                this.xframe = "midair";
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
                    this.self.playSound("gw_jump2");
                    if ((this.self.isFacingRight() && this.self.getControls().LEFT) || (!(this.self.isFacingRight()) && this.self.getControls().RIGHT))
                    {
                        this.self.stancePlayFrame("backflip");
                    };
                };
            };
        }

        internal function frame22():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame43():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

