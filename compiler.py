import ast
from ast import *
from utils import *
from x86_ast import *
import os
import sys
from typing import List, Tuple, Set, Dict

Binding = Tuple[Name, expr]
Temporaries = List[Binding]


class Compiler:

    ############################################################################
    # Remove Complex Operands
    ############################################################################

    def rco_exp(self, e: expr, need_atomic : bool) -> Tuple[expr, Temporaries]:
        # YOUR CODE HERE
        match e:
            case Constant(value):
                return (Constant(value),[])
            case Name(id):
                return (Name(id), [])
            case UnaryOp(USub(), v):
                new_v, bindings = self.rco_exp(v,True)
                new_e = UnaryOp(USub(), new_v)
                if need_atomic:
                    temp_name = generate_name("tmp")
                    return (Name(temp_name), bindings + [(temp_name,new_e)])
                else:
                    return (new_e, bindings)
            case BinOp(left, Add(), right):
                new_l , b1 = self.rco_exp(left,True)
                new_r, b2 = self.rco_exp(right,True)
                new_e = BinOp(new_l,Add(),new_r)
                if need_atomic:
                    temp_name = generate_name("tmp")
                    return (Name(temp_name),b1 +  b2 + [(temp_name, new_e)])
                else:
                    return (new_e,b1 + b2)
            case BinOp(left, Sub(),right):
                new_l , b1 = self.rco_exp(left,True)
                new_r, b2 = self.rco_exp(right,True)
                new_e = BinOp(new_l,Sub(),new_r)
                if need_atomic:
                    temp_name = generate_name("tmp")
                    return (Name(temp_name), b1 + b2 + [(temp_name,new_e)])
                else:
                    return (new_e, b1 + b2)
            case Call(Name('input_int'),[]):
                new_e = Call(Name('input_int'),[])
                if need_atomic:
                    temp_name = generate_name("tmp")
                    return (Name(temp_name),[(temp_name,new_e)])
                else:
                    return (new_e,[])
          
            
                

    def rco_stmt(self, s: stmt) -> List[stmt]:
        # YOUR CODE HERE
        match s:
            case Assign([Name(id)],value):
                new_v, bindings = self.rco_exp(value,False)
                stmts = [Assign([Name(t)],e) for t,e in bindings]
                return stmts + [Assign([Name(id)], new_v)]
            case Expr(Call(Name('print'),[arg])):
                new_arg, bindings = self.rco_exp(arg,True)
                stmts = [Assign([Name(t)],e) for t,e in bindings]
                return stmts + [Expr(Call(Name('print'),[new_arg]))]
            case Expr(exp):
                new_exp, bindings = self.rco_exp(exp,False)
                stmts = [Assign([Name(t)],e) for t,e in bindings]
                return stmts + [Expr(new_exp)]

         

                

    def remove_complex_operands(self, p: Module) -> Module:
        # YOUR CODE HERE
        match p:
            case Module(body):
                new_body = []
                for stmt in body:
                    new_body.extend(self.rco_stmt(stmt))
                  
                return Module(new_body)
                        

    ############################################################################
    # Select Instructions
    ############################################################################

    # The expression e passed to select_arg should furthermore be an atom.
    # (But there is no type for atoms, so the type of e is given as expr.)
    def select_arg(self, e: expr) -> arg:
        # YOUR CODE HERE
        match e:
            case Constant(value):
                return Immediate(value)
            case Name(var):
                return Variable(var)
            

            

            
            
                
            
        
        
        pass        

    def select_stmt(self, s: stmt) -> List[instr]:
        # YOUR CODE HERE
        match s:
            case Assign([Name(var)],UnaryOp(USub(), v)):
                val = self.select_arg(v)
                return [Instr('movq',[val, Reg('rax')]),
                        Instr('negq',[Reg('rax')]),
                        Instr('movq',[Reg('rax'), Variable(var)])]
            case Assign([Name(var)], BinOp(left,Add(), right)):
                l = self.select_arg(left)
                r = self.select_arg(right)
                if isinstance(left, Name) and left.id == var:
                    return [Instr('addq',[r,Variable(var)])]
                elif isinstance(right, Name) and right.id == var:
                    return [Instr('addq',[l,Variable(var)])]
                else:
                    return [Instr('movq',[l, Reg('rax')]),
                        Instr('addq',[r,Reg('rax')]),
                        Instr('movq',[Reg('rax'), Variable(var)])]
            case Assign([Name(var)], BinOp(left, Sub(), right)):
                l = self.select_arg(left)
                r = self.select_arg(right)
                if isinstance(left, Name) and left.id == var:
                    return [Instr('subq',[r,Variable(var)])]
                else:
                    return [Instr('movq',[l,Reg('rax')]),
                        Instr('subq',[r,Reg('rax')]),
                        Instr('movq', [Reg('rax'),Variable(var)])]
            case Assign([Name(var)], Call(Name('input_int'))):
                label = label_name('read_int')
                return [Callq(label,1),
                        Instr('movq', [Reg('rax'), Variable(var)])]
            case Assign([Name(var)], value):
                new_value = self.select_arg(value)
                return [Instr('movq',[new_value, Variable(var)])]
            case Expr(Call(Name('print'),[arg])):
                new_arg = self.select_arg(arg)
                label = label_name("print_int")
                return [Instr('movq',[new_arg, Reg('rdi')]),
                        Callq(label,1)]

            
       
                

    def select_instructions(self, p: Module) -> X86Program:
        # YOUR CODE HERE
        match p:
            case Module(body):
                new_body = []
                for stmt in body:
                    new_body.extend(self.select_stmt(stmt))
                return X86Program(new_body)
                

    ############################################################################
    # Assign Homes
    ############################################################################

    def assign_homes_arg(self, a: arg, home: Dict[Variable, arg]) -> arg:
        # YOUR CODE HERE
        match a:
            case Variable(val):           
                return Deref('rbp',home[Variable(val)])
            case Immediate(val):
                return Immediate(val)
            case Reg(reg):
                return Reg(reg)
            case _:
                return arg
                

    def assign_homes_instr(self, i: instr,
                           home: Dict[Variable, arg]) -> instr:
        # YOUR CODE HERE
        
        match i:
            case Instr('movq',[Immediate(int),Variable(id)]):
                if Variable(id) not in home:
                    home[Variable(id)] = (len(home) + 1) * -8
                return Instr('movq',[self.assign_homes_arg(Immediate(int),home), self.assign_homes_arg(Variable(id), home)])
            case Instr('movq', [Variable(a), Variable(b)]):
                if Variable(b) not in home:
                    home[Variable(id)] = (len(home) + 1) * -8
                return Instr('movq', [self.assign_homes_arg(Variable(a),home) , self.assign_homes_arg(Variable(b),home)])
            case Instr('movq',[Variable(a),Reg(reg)]):
                if Variable(a) not in home:
                    home[Variable(a)] = (len(home) + 1) * -8
                return Instr('movq',[self.assign_homes_arg(Variable(a),home),self.assign_homes_arg(Reg(reg),home)])
            case Instr('movq',[Reg(reg),Variable(id)]):
                if Variable(id) not in home:
                    home[Variable(id)] = (len(home) + 1) * -8
                return Instr('movq',[self.assign_homes_arg(Reg(reg),home), self.assign_homes_arg(Variable(id),home)])
            case Instr('addq',[Immediate(int), Variable(id)]):
                if Variable(id) not in home:
                    home[Variable(id)] = (len(home) + 1) * -8
                return Instr('addq',[self.assign_homes_arg(Immediate(int),home), self.assign_homes_arg(Variable(id),home)])
            case Instr('subq',[Immediate(int),Variable(id)]):
                if Variable(id) not in home:
                    home[Variable(id)] = (len(home) + 1) * -8
                return Instr('subq',[self.assign_homes_arg(Immediate(int),home),self.assign_homes_arg(Variable(id),home)])
            case Instr('addq',[Variable(id), Reg(reg)]):
                if Variable(id) not in home:
                    home[Variable(id)] = (len(home) + 1) * -8
                return Instr('addq',[self.assign_homes_arg(Variable(id),home), self.assign_homes_arg(Reg(reg),home)])
            case Instr('subq',[Variable(id), Reg(reg)]):
                if Variable(id) not in home:
                    home[Variable(id)] = (len(home) + 1) * -8
                return Instr('subq',[self.assign_homes_arg(Variable(id),home), self.assign_homes_arg(Reg(reg),home)])
            case Instr('addq',[Variable(id1),Variable(id2)]):
                if Variable(id1) not in home:
                    home[Variable(id1)] = (len(home) + 1) * -8
                if Variable(id2) not in home:
                    home[Variable(id2)] = (len(home) + 1) * -8
                return Instr('addq',[self.assign_homes_arg(Variable(id1),home), self.assign_homes_arg(Variable(id2),home)])
            case Instr('subq',[Variable(id1),Variable(id2)]):
                if Variable(id1) not in home:
                    home[Variable(id1)] = (len(home)+1) * -8
                if Variable(id2) not in home:
                    home[Variable(id2)] = (len(home) + 1) * -8
                return Instr('subq',[self.assign_homes_arg(Variable(id1),home),self.assign_homes_arg(Variable(id2),home)])
            case _:
                return i
                
                
                

    def assign_homes(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        new_list = []
        home = {}
        for instr in p.body:
            new_list.append(self.assign_homes_instr(instr,home))
        new_program = X86Program(new_list)
        new_program.stack_space = len(home) * 8
        return new_program
               

    ############################################################################
    # Patch Instructions
    ############################################################################

    def patch_instr(self, i: instr) -> List[instr]:
        # YOUR CODE HERE
          match i:
                case Instr('movq',[Deref('rbp',num1),Deref('rbp',num2)]):
                    return [Instr('movq',[Deref('rbp',num1),Reg('rax')]), 
                            Instr('movq',[Reg('rax'),Deref('rbp',num2)])]
                case Instr('addq', [Deref('rbp',num1), Deref('rbp',num2)]):
                    return [Instr('movq',[Deref('rbp',num1),Reg('rax')]),
                            Instr('addq',[Reg('rax'),Deref('rbp',num2)])]
                case Instr('subq',[Deref('rbp',num1),Deref('rbp',num2)]):
                    return [Instr('movq',[Deref('rbp',num1), Reg('rax')]),
                            Instr('subq',[Reg('rax'),Deref('rbp',num2)])]
                case Instr('addq',[Immediate(int), Deref('rbp',num)]):
                    if Immediate(int).value > 2**16:
                        return [Instr('movq',[Immediate(int), Reg('rax')]),
                                Instr('addq',[Reg('rax'),Deref('rbp',num)])]    
                    return [i]
                case Instr('subq',[Immediate(int),Deref('rbp',num)]):       
                    if Immediate(int).value > 2**16:
                        return [Instr('movq',[Immediate(int),Reg('rax')]),
                                Instr('subq',[Reg('rax'),Deref('rbp',num)])]
                    return [i]
                case _:
                    return [i]
                

    def patch_instructions(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        new_list = []
        for instr in p.body:
            new_list.extend(self.patch_instr(instr))
        new_program = X86Program(new_list)
        new_program.stack_space = p.stack_space
        return new_program
           

    ############################################################################
    # Prelude & Conclusion
    ############################################################################

    def prelude_and_conclusion(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        if p.stack_space % 16 != 0:
            p.stack_space += 8
        prelude = [Instr('pushq',[Reg('rbp')]),
                   Instr('movq',[Reg('rsp'),Reg('rbp')]),
                   Instr('subq',[Immediate(p.stack_space),Reg('rsp')])]
        conclusion = [Instr('addq',[Immediate(p.stack_space),Reg('rsp')]),
                      Instr('popq',[Reg('rbp')]),
                      Instr('retq',[])]
        return X86Program(prelude + p.body + conclusion)

def compile():
    compiler = Compiler()
    if(len(sys.argv) != 2):
        print("Number of arguments didn't match")
        sys.exit(1)
    file_path = sys.argv[1]
    with open(file_path,"r") as f:
        code = f.read()

    parsed_code = parse(code)
    rco_code = compiler.remove_complex_operands(parsed_code)
    select_instr_code = compiler.select_instructions(rco_code)
    assign_homes_code = compiler.assign_homes(select_instr_code)
    patch_instr_code = compiler.patch_instructions(assign_homes_code)
    final_program = compiler.prelude_and_conclusion(patch_instr_code)

    output_path = file_path.rsplit(".",1)[0] + ".s"
    with open(output_path,"w") as f:
        f.write(str(final_program))
    
if __name__ == "__main__":
    compile()
    
                

