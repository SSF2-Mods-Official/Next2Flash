package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class FSmash_37 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var xframe:String;

        public function FSmash_37()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 43, this.frame44, 44, this.frame45, 46, this.frame47, 48, this.frame49, 67, this.frame68);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            this.xframe = null;
        }

        internal function frame4():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame44():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame45():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame47():*
        {
            this.self.attachEffect("global_dust_heavy");
            this.self.playAttackSound(1);
            this.self.playVoiceSound(1);
            this.self.addEffectToList(this.self.attachEffect("dee_fsmash_water", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame49():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":13,
                "power":50,
                "kbConstant":96
            });
            this.self.playAttackSound(2);
        }

        internal function frame68():*
        {
            this.self.endAttack();
        }


    }
}

