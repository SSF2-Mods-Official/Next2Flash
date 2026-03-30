package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class SSpecial_109 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var self:KirbyExt;

        public function SSpecial_109()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 13, this.frame14, 30, this.frame31);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.playAttackSound(1);
            };
        }

        internal function frame5():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame14():*
        {
            this.self.playAttackSound(2);
            this.self.playVoiceSound(1);
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(2),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}

