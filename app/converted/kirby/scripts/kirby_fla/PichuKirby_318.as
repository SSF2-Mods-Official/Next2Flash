package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class PichuKirby_318 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:*;
        public var proj:*;

        public function PichuKirby_318()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 9, this.frame10, 10, this.frame11, 11, this.frame12, 28, this.frame29);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getCharacter(this);
        }

        internal function frame2():*
        {
            this.self.playVoiceSound(1);
        }

        internal function frame10():*
        {
            this.self.attachEffect("pichu_elec_nspec", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true
            });
        }

        internal function frame11():*
        {
            this.proj = this.self.fireProjectile("pichuthunderJolt", 0, -15);
            if (this.self.isOnGround())
            {
                if (this.self.isFacingRight())
                {
                    this.proj.angleControl(this.proj.getProjectileStat("xspeed"), 20);
                }
                else
                {
                    this.proj.angleControl(this.proj.getProjectileStat("xspeed"), 160);
                };
            };
            this.self.attachEffect("global_dust_light");
            if (this.self.getCharacterStat("stamina") <= 0)
            {
                this.self.setDamage((this.self.getDamage() + 3));
            }
            else
            {
                this.self.setDamage((this.self.getDamage() - 3));
            };
            this.self.throbDamageCounter();
        }

        internal function frame12():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame29():*
        {
            this.self.endAttack();
        }


    }
}

