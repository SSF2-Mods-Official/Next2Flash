package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Idle_3 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var item:*;
        public var rand:int;
        public var repeats:int;

        public function Idle_3()
        {
            super();
            addFrameScript(0, this.frame1, 25, this.frame26, 51, this.frame52, 66, this.frame67, 80, this.frame81, 91, this.frame92, 92, this.frame93, 94, this.frame95, 95, this.frame96, 120, this.frame121);
        }

        public function backToIdle(_arg_1:*=null):*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame1():*
        {
            var _local_1:* = __activation__;
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            this.item = null;
            this.rand = 0;
            if (this.self && SSF2API.isReady())
            {
                this.self.addEventListener(SSF2Event.STATE_CHANGE, function (_arg_1:*):*
                {
                    if (((_arg_1.data.fromState == 12) && self.getGlobalVariable("crouchdown")) || self.getGlobalVariable("usedDtilt"))
                    {
                        self.setGlobalVariable("crouchdown", false);
                        self.setGlobalVariable("usedDtilt", false);
                        self.stancePlayFrame("uncrouch");
                    }
                    else
                    {
                        self.setGlobalVariable("crouchdown", false);
                        self.setGlobalVariable("usedDtilt", false);
                    };
                });
                if (!this.self.getItem())
                {
                    this.self.stancePlayFrame("loop");
                    if (this.repeats >= 3)
                    {
                        this.rand = (10 * SSF2API.random());
                        if (this.rand >= 5)
                        {
                            this.repeats = 0;
                            this.gotoAndStop("blink");
                        };
                        if (this.rand >= 8)
                        {
                            this.repeats = 0;
                            this.gotoAndStop("wait");
                        };
                    };
                }
                else
                {
                    this.self.stancePlayFrame("item_loop");
                };
            };
        }

        internal function frame26():*
        {
            this.repeats++;
            this.gotoAndStop("loop");
        }

        internal function frame52():*
        {
            this.repeats++;
            this.gotoAndStop("loop");
        }

        internal function frame67():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_idleBelly");
            };
        }

        internal function frame81():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_idleBelly");
            };
        }

        internal function frame92():*
        {
            if (!this.self.getItem())
            {
                this.self.stancePlayFrame("loop");
            }
            else
            {
                this.self.stancePlayFrame("item_loop");
            };
        }

        internal function frame93():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_step02");
        }

        internal function frame95():*
        {
            if (!this.self.getItem())
            {
                this.self.stancePlayFrame("loop");
            }
            else
            {
                this.self.stancePlayFrame("item_loop");
            };
            this.self.playSound("ssf2_snd_sfx_dedede_step01");
        }

        internal function frame96():*
        {
            if (this.item)
            {
                this.self.addEventListener(SSF2Event.ITEM_TOSSED, this.backToIdle);
            };
            if (this.repeats >= 3)
            {
                this.rand = (10 * SSF2API.random());
                if (this.rand >= 8)
                {
                    this.repeats = 0;
                    this.gotoAndStop("wait");
                };
            };
        }

        internal function frame121():*
        {
            this.repeats++;
            this.gotoAndStop("item_loop");
        }


    }
}

