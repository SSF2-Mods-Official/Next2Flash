package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class DTilt_143 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function DTilt_143()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 7, this.frame8, 11, this.frame12);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
        }

        internal function frame3():*
        {
            this.self.setXSpeed(10, false);
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-1),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
            this.self.playAttackSound(1);
        }

        internal function frame8():*
        {
            this.self.setXSpeed(-4, false);
        }

        internal function frame12():*
        {
            this.self.endAttack();
        }


    }
}

