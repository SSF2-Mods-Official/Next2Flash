package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class DoubleJump_21 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var done:*;

        public function DoubleJump_21()
        {
            super();
            addFrameScript(0, this.frame1, 16, this.frame17, 21, this.frame22, 22, this.frame23);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            this.done = false;
            if (SSF2API.isReady() && this.self)
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
                    this.self.updateAuraPaws();
                };
            };
        }

        internal function frame17():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame22():*
        {
            this.done = true;
            stop();
        }

        internal function frame23():*
        {
            this.self.stancePlayFrame("done");
        }


    }
}

