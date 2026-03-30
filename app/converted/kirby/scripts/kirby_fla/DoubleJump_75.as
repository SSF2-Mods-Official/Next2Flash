package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class DoubleJump_75 extends MovieClip
    {

        public var hand:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function DoubleJump_75()
        {
            super();
            addFrameScript(0, this.frame1, 16, this.frame17, 33, this.frame34, 50, this.frame51);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
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
                    if (this.self.isFacingRight() && this.self.getControls().LEFT)
                    {
                        this.self.faceLeft();
                        this.self.stancePlayFrame("jumpLeft");
                    }
                    else if (!(this.self.isFacingRight()) && this.self.getControls().RIGHT)
                    {
                        this.self.faceRight();
                        this.self.stancePlayFrame("jumpRight");
                    };
                    if (this.self.getMidairJumpCount() == 1)
                    {
                        this.self.playSound("ssf2_snd_sfx_kirby_jump02");
                    }
                    else if (this.self.getMidairJumpCount() == 2)
                    {
                        this.self.playSound("ssf2_snd_sfx_kirby_jump03");
                    }
                    else if (this.self.getMidairJumpCount() == 3)
                    {
                        this.self.playSound("ssf2_snd_sfx_kirby_jump04");
                    }
                    else if (this.self.getMidairJumpCount() == 4)
                    {
                        this.self.playSound("ssf2_snd_sfx_kirby_jump05");
                    }
                    else if (this.self.getMidairJumpCount() == 5)
                    {
                        this.self.playSound("ssf2_snd_sfx_kirby_jump06");
                    };
                };
            };
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }

        internal function frame34():*
        {
            this.self.endAttack();
        }

        internal function frame51():*
        {
            this.self.endAttack();
        }


    }
}

