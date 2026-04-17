package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_jumpMidair_30 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function fox_jumpMidair_30()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 11, this.frame12, 18, this.frame19);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.prevAnim = false;
                if (this.self.getGlobalVariable("screwAttackOn") && (this.self.getMidairJumpCount() < 2))
                {
                    this.self.forceAttack("item_screw");
                }
                else
                {
                    if (this.self.getGlobalVariable("sonicShieldFiredash") && (this.self.getControls().LEFT || this.self.getControls().RIGHT))
                    {
                        this.self.forceAttack("item_firedash");
                    }
                    else
                    {
                        if (this.self.getGlobalVariable("sonicShieldBubbleBounce") && this.self.getControls().DOWN)
                        {
                            this.self.forceAttack("item_bubblebounce");
                        }
                        else
                        {
                            this.self.playSound("fox_jump02");
                        };
                    };
                };
            };
        }

        internal function frame6():*
        {
            this.self.playSound("fox_jumpflip");
        }

        internal function frame12():*
        {
            this.self.playSound("fox_jumpflip");
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }


    }
}

