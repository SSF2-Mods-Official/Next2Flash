package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class DoubleJump_42 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var done:Boolean;

        public function DoubleJump_42()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 18, this.frame19, 27, this.frame28, 41, this.frame42);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            if (SSF2API.isReady() && this.self)
            {
                this.done = false;
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
                    this.self.playSound("falcon_jumpS2");
                    this.self.setGlobalVariable("nStoredLabel", null);
                    this.self.setGlobalVariable("sStoredLabel", null);
                };
                if ((this.self.isFacingRight() && this.self.getControls().LEFT) || (!(this.self.isFacingRight()) && this.self.getControls().RIGHT))
                {
                    this.self.stancePlayFrame("backflip");
                };
            };
        }

        internal function frame6():*
        {
            this.self.playSound("cf_midairflip");
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }

        internal function frame28():*
        {
            this.self.playSound("cf_midairflip");
        }

        internal function frame42():*
        {
            this.self.endAttack();
        }


    }
}

